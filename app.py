from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from typing import List, Optional, Dict
from pydantic import BaseModel
import pandas as pd
import json
import logging
from datetime import date

# Import the module so we can access attributes dynamically (helps with testing/patching)
import src.core.db
from src.core.db import get_session, create_db_and_tables
from src.core.models import Player, PlayerStats, FantasyTeam, TeamRoster, League, DailyStandings
from src.ingestion.nba_client import NBAClient
from src.core.stats import aggregate_player_stats, calculate_z_scores
from src.core.analyzer import TradeAnalyzer
from src.core.recommender import recommend_daily_lineup
from src.core.roto import calculate_roto_standings
from src.core.importer import RosterImporter

app = FastAPI(title="Fantasy NBA Assistant API")

@app.on_event("startup")
def on_startup():
    try:
        create_db_and_tables()
    except Exception as e:
        print(f"WARNING: Database connection failed on startup: {e}")
        logging.warning(f"Database connection failed: {e}")

# Models for API
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

class PlayerAdd(BaseModel):
    player_id: int

class RosterImportRequest(BaseModel):
    roster_map: Dict[str, List[str]] # {"TeamName": ["Player1", "Player2"]}

@app.get("/")
def read_root():
    return {"message": "Welcome to Fantasy NBA Assistant"}

@app.post("/ingest")
def trigger_ingestion(req: IngestionRequest, background_tasks: BackgroundTasks):
    client = NBAClient()
    # Access engine dynamically from the module to pick up any test patches
    background_tasks.add_task(client.sync_players, src.core.db.engine, mock=req.mock)
    background_tasks.add_task(client.sync_recent_stats, src.core.db.engine, days=req.days, mock=req.mock)
    return {"status": "Ingestion started in background"}

@app.get("/players")
def get_players(session: Session = Depends(get_session)):
    players = session.exec(select(Player)).all()
    return players

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

# --- League Management ---
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

@app.get("/leagues/{league_id}/standings", response_model=List[DailyStandings])
def get_standings(league_id: int, session: Session = Depends(get_session)):
    # Trigger Calculation (in a real app this might be a background job)
    standings = calculate_roto_standings(session, league_id)
    # Re-fetch ensuring relations if needed, or just return list
    # Because calculate_roto_standings returns objects attached to session, simple return works
    # However, sort by rank
    return sorted(standings, key=lambda x: x.rank)

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

@app.post("/leagues/{league_id}/import_rosters")
def import_rosters(league_id: int, req: RosterImportRequest, session: Session = Depends(get_session)):
    importer = RosterImporter(session)
    report = importer.process_import(league_id, req.roster_map)
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])
    return report

# --- Team Management ---
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
