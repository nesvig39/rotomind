from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from src.api.app import app, get_session
import pytest
import os
import tempfile
import src.core.db  # Import to override engine

# Use a temporary file for the test DB to avoid permission issues
# and ensure clean state
test_db_fd, test_db_path = tempfile.mkstemp(suffix=".db")
sqlite_url = f"sqlite:///{test_db_path}"

# Create a Test Engine (SQLite)
test_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

# Override the global engine in src.core.db so that create_db_and_tables uses it
# This is critical because app.on_startup imports and uses src.core.db.engine
src.core.db.engine = test_engine

def get_test_session():
    with Session(test_engine) as session:
        yield session

app.dependency_overrides[get_session] = get_test_session

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
    # Test triggering ingestion
    response = client.post("/ingest", json={"days": 5, "mock": True})
    assert response.status_code == 200
    assert response.json() == {"status": "Ingestion started in background"}
    
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
    # Ingest data first so we have players
    client.post("/ingest", json={"days": 5, "mock": True})
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
    # Ingest mock data
    client.post("/ingest", json={"days": 5, "mock": True})
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
    
    # Calculate Standings
    s_res = client.get(f"/leagues/{league_id}/standings")
    assert s_res.status_code == 200
    standings = s_res.json()
    
    assert len(standings) == 2
    # Check if points are assigned (should be 1 and 2 if stats differ)
    # Mock stats are random, so rank might vary, but total_roto_points should be > 0
    assert standings[0]['total_roto_points'] > 0

def test_roster_import(client):
    # Ingest mock data
    client.post("/ingest", json={"days": 5, "mock": True})
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
        "Lakers": ["Lebron James", "Unknown Player"]
    }
    
    res = client.post(f"/leagues/{league_id}/import_rosters", json={"roster_map": roster_map})
    assert res.status_code == 200
    report = res.json()
    
    assert report["teams_created"] == 2
    assert report["players_added"] == 2 # Steph and Lebron
    assert len(report["players_not_found"]) == 1
    assert report["players_not_found"][0]["player"] == "Unknown Player"
    
    # Verify Roster
    teams = client.get("/teams").json()
    warriors = next(t for t in teams if t["name"] == "Warriors")
    assert warriors["league_id"] == league_id
    
    p_res = client.get(f"/teams/{warriors['id']}/players").json()
    assert len(p_res) == 1
    assert "Curry" in p_res[0]["full_name"]

def test_recommender(client):
    client.post("/ingest", json={"days": 5, "mock": True})
    players = client.get("/players").json()
    
    if len(players) < 3:
         pytest.skip("Not enough players for recommender test")

    ids = [p['id'] for p in players[:3]]
    
    response = client.post("/recommend/lineup", json=ids)
    assert response.status_code == 200
    recommendations = response.json()
    assert len(recommendations) == 3
    # Check if sorted by z_total descending
    z_scores = [r['z_total'] for r in recommendations]
    assert z_scores == sorted(z_scores, reverse=True)
