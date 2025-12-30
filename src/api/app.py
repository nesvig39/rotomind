from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import pandas as pd
import json
import logging
from datetime import date

import src.core.db
from src.core.db import get_session, create_db_and_tables
from src.core.models import Player, PlayerStats, FantasyTeam, TeamRoster, League, DailyStandings, AgentTask
from src.core.stats import aggregate_player_stats, calculate_z_scores
from src.core.analyzer import TradeAnalyzer
from src.core.recommender import recommend_daily_lineup
from src.core.supervisor import Supervisor

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    try:
        create_db_and_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.warning(f"Database connection failed on startup: {e}")
    
    yield  # Application runs here
    
    # Shutdown (cleanup if needed)
    logger.info("Application shutting down")


app = FastAPI(title="Fantasy NBA Assistant API", lifespan=lifespan)

# Models
class TradeRequest(BaseModel):
    team_a_roster: Optional[List[int]] = None
    team_b_roster: Optional[List[int]] = None
    team_a_id: Optional[int] = None
    team_b_id: Optional[int] = None
    players_to_b: List[int]
    players_to_a: List[int]

class IngestionRequest(BaseModel):
    days: int = 15
    mock: bool = False

class TeamCreate(BaseModel):
    name: str
    owner_name: Optional[str] = None
    league_id: Optional[int] = None

class LeagueCreate(BaseModel):
    name: str
    season: str = "2024-25"
    espn_league_id: Optional[int] = None
    espn_s2: Optional[str] = None
    espn_swid: Optional[str] = None


class ESPNConfigUpdate(BaseModel):
    """Update ESPN integration settings for a league."""
    espn_league_id: int
    espn_s2: str
    espn_swid: str


class HybridSyncRequest(BaseModel):
    """Request for hybrid ESPN + NBA sync."""
    sync_nba_players: bool = True
    sync_nba_stats: bool = True
    sync_espn_rosters: bool = True
    limit_nba_players: Optional[int] = None
    mock_nba: bool = False

class PlayerAdd(BaseModel):
    player_id: int

class RosterImportRequest(BaseModel):
    roster_map: Dict[str, List[str]]

class TaskResponse(BaseModel):
    task_id: str
    status: str

@app.get("/")
def read_root():
    return {"message": "Welcome to Fantasy NBA Assistant"}

# --- Supervisor / Agent Endpoints ---

@app.post("/ingest", response_model=TaskResponse)
def trigger_ingestion(req: IngestionRequest, background_tasks: BackgroundTasks):
    task = Supervisor.submit_task("ingest_data", req.model_dump())
    background_tasks.add_task(Supervisor.run_task, task.id)
    return {"task_id": task.id, "status": "submitted"}

@app.post("/leagues/{league_id}/import_rosters", response_model=TaskResponse)
def import_rosters(league_id: int, req: RosterImportRequest, background_tasks: BackgroundTasks):
    payload = {"league_id": league_id, "roster_map": req.roster_map}
    task = Supervisor.submit_task("import_roster", payload)
    background_tasks.add_task(Supervisor.run_task, task.id)
    return {"task_id": task.id, "status": "submitted"}

@app.get("/leagues/{league_id}/standings") # Keeping return type flexible as it might be list or task
def get_standings(league_id: int, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    """
    Triggers calculation and returns current (potentially stale) standings immediately.
    Or we could make this purely async.
    For MVP hybrid: Trigger calc in background, return current DB rows.
    """
    # Trigger Update
    task = Supervisor.submit_task("calculate_roto", {"league_id": league_id})
    background_tasks.add_task(Supervisor.run_task, task.id)
    
    # Return current rows
    stmt = select(DailyStandings).where(DailyStandings.league_id == league_id)
    # Sort by date desc, rank asc
    # Actually just get latest date?
    # Simple sort for now
    standings = session.exec(stmt).all()
    return sorted(standings, key=lambda x: (x.date, x.rank), reverse=True)

@app.get("/tasks/{task_id}", response_model=AgentTask)
def get_task_status(task_id: str, session: Session = Depends(get_session)):
    task = session.get(AgentTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# --- ESPN Integration Endpoints ---

@app.post("/leagues/{league_id}/configure_espn")
def configure_espn(
    league_id: int, 
    config: ESPNConfigUpdate, 
    session: Session = Depends(get_session)
):
    """
    Configure ESPN integration for a league.
    
    To get ESPN cookies:
    1. Log into ESPN Fantasy Basketball in your browser
    2. Open Developer Tools (F12) → Application → Cookies
    3. Copy the values for 'espn_s2' and 'SWID'
    """
    league = session.get(League, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    league.espn_league_id = config.espn_league_id
    league.espn_s2 = config.espn_s2
    league.espn_swid = config.espn_swid
    
    session.add(league)
    session.commit()
    session.refresh(league)
    
    return {
        "message": f"ESPN integration configured for league '{league.name}'",
        "espn_league_id": league.espn_league_id,
    }


@app.post("/leagues/{league_id}/hybrid_sync", response_model=TaskResponse)
def trigger_hybrid_sync(
    league_id: int,
    req: HybridSyncRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """
    Trigger a hybrid sync (ESPN rosters + NBA stats) for a league.
    
    This combines:
    - ESPN: Rosters (who owns which players)
    - NBA.com: Player statistics (game-by-game data)
    
    The league must have ESPN credentials configured first.
    """
    league = session.get(League, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    payload = {
        "league_id": league_id,
        "sync_nba_players": req.sync_nba_players,
        "sync_nba_stats": req.sync_nba_stats,
        "sync_espn_rosters": req.sync_espn_rosters,
        "limit_nba_players": req.limit_nba_players,
        "mock_nba": req.mock_nba,
    }
    
    task = Supervisor.submit_task("hybrid_sync", payload)
    background_tasks.add_task(Supervisor.run_task, task.id)
    
    return {"task_id": task.id, "status": "submitted"}


@app.post("/leagues/{league_id}/espn_sync", response_model=TaskResponse)
def trigger_espn_roster_sync(
    league_id: int,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """
    Quick sync of rosters from ESPN (without re-syncing NBA stats).
    
    Use this for fast roster updates after trades/waiver moves.
    The league must have ESPN credentials configured.
    """
    league = session.get(League, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    if not league.espn_league_id:
        raise HTTPException(
            status_code=400, 
            detail="ESPN not configured for this league. Use /configure_espn first."
        )
    
    task = Supervisor.submit_task("espn_roster_sync", {"league_id": league_id})
    background_tasks.add_task(Supervisor.run_task, task.id)
    
    return {"task_id": task.id, "status": "submitted"}


@app.get("/leagues/{league_id}/espn_status")
def get_espn_status(league_id: int, session: Session = Depends(get_session)):
    """
    Get ESPN integration status for a league.
    """
    league = session.get(League, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    
    return {
        "league_id": league.id,
        "league_name": league.name,
        "espn_configured": league.espn_league_id is not None,
        "espn_league_id": league.espn_league_id,
        "last_sync": league.last_espn_sync.isoformat() if league.last_espn_sync else None,
        "credentials_set": bool(league.espn_s2 and league.espn_swid),
    }


# --- Standard Read Endpoints (Direct DB Access) ---

@app.get("/players")
def get_players(
    session: Session = Depends(get_session),
    active_only: bool = True,
    limit: int = 100,
    offset: int = 0,
):
    """Get all players with optional filtering."""
    stmt = select(Player)
    if active_only:
        stmt = stmt.where(Player.is_active == True)
    stmt = stmt.offset(offset).limit(limit)
    players = session.exec(stmt).all()
    return players


@app.get("/players/{player_id}")
def get_player_detail(player_id: int, session: Session = Depends(get_session)):
    """
    Get detailed player information including recent stats.
    
    Returns combined data from NBA and ESPN sources.
    """
    from src.ingestion.hybrid_client import HybridDataClient
    
    player = session.get(Player, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    client = HybridDataClient()
    combined_data = client.get_combined_player_data(session, player_id)
    
    return combined_data

@app.get("/stats")
def get_stats(session: Session = Depends(get_session)):
    stats = session.exec(select(PlayerStats)).all()
    if not stats:
        return []
    data = [s.model_dump() for s in stats]
    df_agg = aggregate_player_stats(data)
    if df_agg.empty:
        return []
    df_z = calculate_z_scores(df_agg)
    players = session.exec(select(Player)).all()
    p_map = {p.id: p.full_name for p in players}
    df_z['full_name'] = df_z['player_id'].map(p_map)
    return df_z.to_dict(orient='records')

@app.post("/leagues", response_model=League)
def create_league(league: LeagueCreate, session: Session = Depends(get_session)):
    db_league = League.model_validate(league)
    session.add(db_league)
    session.commit()
    session.refresh(db_league)
    return db_league

@app.get("/leagues", response_model=List[League])
def get_leagues(session: Session = Depends(get_session)):
    return session.exec(select(League)).all()

@app.post("/leagues/{league_id}/join")
def join_league(league_id: int, team_id: int, session: Session = Depends(get_session)):
    league = session.get(League, league_id)
    team = session.get(FantasyTeam, team_id)
    if not league or not team:
        raise HTTPException(status_code=404, detail="League or Team not found")
    team.league_id = league.id
    session.add(team)
    session.commit()
    return {"message": f"Team {team.name} joined League {league.name}"}

@app.post("/teams", response_model=FantasyTeam)
def create_team(team: TeamCreate, session: Session = Depends(get_session)):
    db_team = FantasyTeam.model_validate(team)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team

@app.get("/teams", response_model=List[FantasyTeam])
def get_teams(session: Session = Depends(get_session)):
    teams = session.exec(select(FantasyTeam)).all()
    return teams

@app.get("/teams/{team_id}", response_model=FantasyTeam)
def get_team(team_id: int, session: Session = Depends(get_session)):
    team = session.get(FantasyTeam, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@app.get("/teams/{team_id}/players", response_model=List[Player])
def get_team_players(team_id: int, session: Session = Depends(get_session)):
    team = session.get(FantasyTeam, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team.players

@app.post("/teams/{team_id}/add_player")
def add_player_to_team(team_id: int, player: PlayerAdd, session: Session = Depends(get_session)):
    team = session.get(FantasyTeam, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    db_player = session.get(Player, player.player_id)
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    if db_player in team.players:
        return {"message": "Player already in team"}
    team.players.append(db_player)
    session.add(team)
    session.commit()
    return {"message": "Player added", "team_id": team.id, "player_id": db_player.id}

@app.post("/analyze/trade")
def analyze_trade(req: TradeRequest, session: Session = Depends(get_session)):
    stats = session.exec(select(PlayerStats)).all()
    if not stats:
        raise HTTPException(status_code=400, detail="No stats available. Run ingestion first.")
    data = [s.model_dump() for s in stats]
    df_agg = aggregate_player_stats(data)
    df_z = calculate_z_scores(df_agg)
    
    roster_a = req.team_a_roster
    roster_b = req.team_b_roster
    
    if req.team_a_id:
        team_a = session.get(FantasyTeam, req.team_a_id)
        if team_a:
            roster_a = [p.id for p in team_a.players]
    if req.team_b_id:
        team_b = session.get(FantasyTeam, req.team_b_id)
        if team_b:
            roster_b = [p.id for p in team_b.players]
            
    if not roster_a or not roster_b:
        raise HTTPException(status_code=400, detail="Must provide either roster IDs or valid team IDs")
    
    analyzer = TradeAnalyzer(df_z)
    result = analyzer.analyze_trade(
        roster_a,
        roster_b,
        req.players_to_b,
        req.players_to_a
    )
    return result

@app.post("/recommend/lineup")
def recommend_lineup(roster_ids: List[int], session: Session = Depends(get_session)):
    stats = session.exec(select(PlayerStats).where(PlayerStats.player_id.in_(roster_ids))).all()
    if not stats:
         return {"message": "No data for these players"}
    data = [s.model_dump() for s in stats]
    df_agg = aggregate_player_stats(data)
    df_z = calculate_z_scores(df_agg)
    players = session.exec(select(Player).where(Player.id.in_(roster_ids))).all()
    p_map = {p.id: p.full_name for p in players}
    df_z['full_name'] = df_z['player_id'].map(p_map)
    recommendation = recommend_daily_lineup(df_z)
    return recommendation.to_dict(orient='records')
