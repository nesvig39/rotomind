from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app import app
from db import get_session
import pytest
import os
import tempfile
import time
import db as db_module  # Import to override engine

# Use a temporary file for the test DB to avoid permission issues
# and ensure clean state
test_db_fd, test_db_path = tempfile.mkstemp(suffix=".db")
sqlite_url = f"sqlite:///{test_db_path}"

# Create a Test Engine (SQLite)
test_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

# Override the global engine in db module so that create_db_and_tables uses it
# This is critical because app startup uses db_module.engine
db_module.engine = test_engine


def get_test_session():
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = get_test_session


def wait_for_task(client, task_id: str, max_attempts: int = 10) -> dict:
    """Helper to poll task until completion."""
    for _ in range(max_attempts):
        response = client.get(f"/tasks/{task_id}")
        if response.status_code == 200:
            task = response.json()
            if task["status"] in ["completed", "failed"]:
                return task
        time.sleep(0.1)
    return None


@pytest.fixture(name="client")
def client_fixture():
    # Create tables in the test database
    SQLModel.metadata.create_all(test_engine)

    with TestClient(app) as client:
        yield client

    # Teardown
    SQLModel.metadata.drop_all(test_engine)


# Cleanup after all tests
@pytest.fixture(scope="session", autouse=True)
def cleanup_db():
    yield
    os.close(test_db_fd)
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


def test_ingest_endpoint(client):
    """Test triggering ingestion and verify data is loaded."""
    response = client.post("/ingest", json={"days": 5, "mock": True})
    assert response.status_code == 200
    
    # API returns a task response
    result = response.json()
    assert "task_id" in result
    assert result["status"] == "submitted"
    
    # Wait for task completion (background tasks run inline in TestClient)
    task = wait_for_task(client, result["task_id"])
    assert task is not None
    assert task["status"] == "completed"

    # Verify players were added (Mock mode adds 5 players)
    response = client.get("/players")
    assert response.status_code == 200
    players = response.json()
    assert len(players) > 0

    # Verify stats were added
    response = client.get("/stats")
    assert response.status_code == 200
    stats = response.json()
    assert len(stats) > 0


def test_team_management(client):
    """Test team creation and player management."""
    # Ingest data first so we have players
    ingest_response = client.post("/ingest", json={"days": 5, "mock": True})
    task_id = ingest_response.json()["task_id"]
    wait_for_task(client, task_id)
    
    players = client.get("/players").json()
    if not players:
        pytest.skip("No players found")

    # Create Team
    response = client.post("/teams", json={"name": "Test Team", "owner_name": "Tester"})
    assert response.status_code == 200
    team = response.json()
    assert team["name"] == "Test Team"
    team_id = team["id"]

    # Add Player
    p_id = players[0]["id"]
    response = client.post(f"/teams/{team_id}/add_player", json={"player_id": p_id})
    assert response.status_code == 200

    # Verify Player in Team
    response = client.get(f"/teams/{team_id}/players")
    assert response.status_code == 200
    team_players = response.json()
    assert len(team_players) == 1
    assert team_players[0]["id"] == p_id


def test_league_standings(client):
    """Test league standings calculation."""
    # Ingest mock data
    ingest_response = client.post("/ingest", json={"days": 5, "mock": True})
    task_id = ingest_response.json()["task_id"]
    wait_for_task(client, task_id)
    
    players = client.get("/players").json()
    if len(players) < 2:
        pytest.skip("Not enough players for league test")

    # Create League
    l_res = client.post("/leagues", json={"name": "Test League"})
    assert l_res.status_code == 200
    league_id = l_res.json()["id"]

    # Create 2 Teams
    t1 = client.post("/teams", json={"name": "Team A", "league_id": league_id}).json()
    t2 = client.post("/teams", json={"name": "Team B", "league_id": league_id}).json()

    # Add different players
    client.post(f"/teams/{t1['id']}/add_player", json={"player_id": players[0]['id']})
    client.post(f"/teams/{t2['id']}/add_player", json={"player_id": players[1]['id']})

    # First call triggers background task and returns empty/stale standings
    s_res = client.get(f"/leagues/{league_id}/standings")
    assert s_res.status_code == 200
    
    # Wait a moment for background task to complete, then fetch again
    time.sleep(0.5)
    
    # Second call should return the calculated standings
    s_res = client.get(f"/leagues/{league_id}/standings")
    assert s_res.status_code == 200
    standings = s_res.json()

    # Standings should have 2 teams
    assert len(standings) == 2
    # Check if points are assigned (should be 1 and 2 if stats differ)
    # Mock stats are random, so rank might vary, but total_roto_points should be > 0
    assert standings[0]["total_roto_points"] > 0


def test_roster_import(client):
    """Test bulk roster import with fuzzy player matching."""
    # Ingest mock data
    ingest_response = client.post("/ingest", json={"days": 5, "mock": True})
    task_id = ingest_response.json()["task_id"]
    wait_for_task(client, task_id)
    
    players = client.get("/players").json()
    if not players:
        pytest.skip("No players found")

    # Create League
    l_res = client.post("/leagues", json={"name": "Import League"})
    league_id = l_res.json()["id"]

    # Prepare Map (Using fuzzy names)
    # Mock players are: Stephen Curry, LeBron James, Nikola Jokic, Luka Doncic, Giannis Antetokounmpo
    roster_map = {
        "Warriors": ["Steph Curry"],
        "Lakers": ["Lebron James", "Unknown Player"],
    }

    res = client.post(f"/leagues/{league_id}/import_rosters", json={"roster_map": roster_map})
    assert res.status_code == 200
    
    # API returns a task response
    result = res.json()
    assert "task_id" in result
    assert result["status"] == "submitted"
    
    # Wait for task completion
    task = wait_for_task(client, result["task_id"])
    assert task is not None
    assert task["status"] == "completed"
    
    # Check the task result for import details
    report = task.get("result", {})
    assert report.get("teams_created") == 2
    assert report.get("players_added") == 2  # Steph and Lebron
    assert len(report.get("players_not_found", [])) == 1
    assert report["players_not_found"][0]["player"] == "Unknown Player"

    # Verify Roster
    teams = client.get("/teams").json()
    warriors = next(t for t in teams if t["name"] == "Warriors")
    assert warriors["league_id"] == league_id

    p_res = client.get(f"/teams/{warriors['id']}/players").json()
    assert len(p_res) == 1
    assert "Curry" in p_res[0]["full_name"]


def test_recommender(client):
    """Test lineup recommendation based on Z-scores."""
    ingest_response = client.post("/ingest", json={"days": 5, "mock": True})
    task_id = ingest_response.json()["task_id"]
    wait_for_task(client, task_id)
    
    players = client.get("/players").json()

    if len(players) < 3:
        pytest.skip("Not enough players for recommender test")

    ids = [p["id"] for p in players[:3]]

    response = client.post("/recommend/lineup", json=ids)
    assert response.status_code == 200
    recommendations = response.json()
    assert len(recommendations) == 3
    # Check if sorted by z_total descending
    z_scores = [r["z_total"] for r in recommendations]
    assert z_scores == sorted(z_scores, reverse=True)


def test_trade_analyzer(client):
    """Test trade analysis endpoint."""
    ingest_response = client.post("/ingest", json={"days": 5, "mock": True})
    task_id = ingest_response.json()["task_id"]
    wait_for_task(client, task_id)
    
    players = client.get("/players").json()
    if len(players) < 4:
        pytest.skip("Not enough players for trade test")

    # Create two teams
    t1 = client.post("/teams", json={"name": "Trade Team A"}).json()
    t2 = client.post("/teams", json={"name": "Trade Team B"}).json()

    # Add players to teams
    client.post(f"/teams/{t1['id']}/add_player", json={"player_id": players[0]["id"]})
    client.post(f"/teams/{t1['id']}/add_player", json={"player_id": players[1]["id"]})
    client.post(f"/teams/{t2['id']}/add_player", json={"player_id": players[2]["id"]})
    client.post(f"/teams/{t2['id']}/add_player", json={"player_id": players[3]["id"]})

    # Analyze trade
    trade_request = {
        "team_a_id": t1["id"],
        "team_b_id": t2["id"],
        "players_to_b": [players[0]["id"]],
        "players_to_a": [players[2]["id"]],
    }

    response = client.post("/analyze/trade", json=trade_request)
    assert response.status_code == 200
    result = response.json()
    
    assert "team_a" in result
    assert "team_b" in result
    assert "before" in result["team_a"]
    assert "after" in result["team_a"]
    assert "diff" in result["team_a"]
