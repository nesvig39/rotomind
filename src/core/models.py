from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, Relationship, JSON, UniqueConstraint
from sqlalchemy import Index
from datetime import date, datetime, timezone
import uuid


def utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


# Link table for Many-to-Many relationship
class TeamRoster(SQLModel, table=True):
    """Junction table for fantasy team rosters."""
    __tablename__ = "teamroster"
    
    team_id: Optional[int] = Field(default=None, foreign_key="fantasyteam.id", primary_key=True)
    player_id: Optional[int] = Field(default=None, foreign_key="player.id", primary_key=True)
    added_at: datetime = Field(default_factory=utc_now)


class League(SQLModel, table=True):
    """Fantasy league configuration with optional ESPN integration."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    season: str = "2024-25"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    
    # ESPN integration fields
    espn_league_id: Optional[int] = Field(default=None, index=True)  # ESPN league ID
    espn_s2: Optional[str] = Field(default=None)  # ESPN authentication cookie
    espn_swid: Optional[str] = Field(default=None)  # ESPN SWID cookie
    last_espn_sync: Optional[datetime] = Field(default=None)  # Last successful sync
    
    teams: List["FantasyTeam"] = Relationship(back_populates="league")


class Player(SQLModel, table=True):
    """NBA player information with optional ESPN integration."""
    id: int = Field(default=None, primary_key=True)
    nba_id: int = Field(unique=True, index=True)
    espn_id: Optional[int] = Field(default=None, unique=True, index=True)  # ESPN player ID
    full_name: str = Field(index=True)  # Index for name lookups
    team_abbreviation: Optional[str] = Field(default=None, index=True)
    position: Optional[str] = None
    is_active: bool = Field(default=True, index=True)  # Index for filtering active players
    
    # ESPN-specific data (updated during ESPN sync)
    espn_ownership_pct: Optional[float] = Field(default=None)  # % owned in ESPN leagues
    espn_injury_status: Optional[str] = Field(default=None)  # OUT, GTD, etc.
    
    stats: List["PlayerStats"] = Relationship(back_populates="player")
    teams: List["FantasyTeam"] = Relationship(back_populates="players", link_model=TeamRoster)


class PlayerStats(SQLModel, table=True):
    """Individual game statistics for a player."""
    __tablename__ = "playerstats"
    __table_args__ = (
        # Composite unique constraint to prevent duplicate game entries
        UniqueConstraint("player_id", "game_id", name="uq_player_game"),
        # Composite index for common query patterns
        Index("ix_playerstats_player_date", "player_id", "game_date"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="player.id", index=True)
    game_date: date = Field(index=True)
    game_id: str = Field(index=True)
    matchup: str
    pts: int = Field(default=0, ge=0)  # Greater than or equal to 0
    reb: int = Field(default=0, ge=0)
    ast: int = Field(default=0, ge=0)
    stl: int = Field(default=0, ge=0)
    blk: int = Field(default=0, ge=0)
    fgm: int = Field(default=0, ge=0)
    fga: int = Field(default=0, ge=0)
    ftm: int = Field(default=0, ge=0)
    fta: int = Field(default=0, ge=0)
    tpm: int = Field(default=0, ge=0)
    tov: int = Field(default=0, ge=0)
    
    player: Player = Relationship(back_populates="stats")

class FantasyTeam(SQLModel, table=True):
    """Fantasy team with optional ESPN integration."""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    owner_name: Optional[str] = None
    league_id: Optional[int] = Field(default=None, foreign_key="league.id")
    
    # ESPN integration
    espn_team_id: Optional[int] = Field(default=None, index=True)  # ESPN team ID
    
    players: List[Player] = Relationship(back_populates="teams", link_model=TeamRoster)
    league: Optional[League] = Relationship(back_populates="teams")
    daily_standings: List["DailyStandings"] = Relationship(back_populates="team")

class DailyStandings(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="fantasyteam.id")
    league_id: int = Field(foreign_key="league.id")
    date: date
    
    # Raw Totals
    total_pts: int = 0
    total_reb: int = 0
    total_ast: int = 0
    total_stl: int = 0
    total_blk: int = 0
    total_fgm: int = 0
    total_fga: int = 0
    total_ftm: int = 0
    total_fta: int = 0
    total_tpm: int = 0
    
    # Roto Points (Rank) - Floats for ties
    points_pts: float = 0.0
    points_reb: float = 0.0
    points_ast: float = 0.0
    points_stl: float = 0.0
    points_blk: float = 0.0
    points_fg_pct: float = 0.0
    points_ft_pct: float = 0.0
    points_tpm: float = 0.0
    
    total_roto_points: float = 0.0
    rank: int = 0
    
    team: FantasyTeam = Relationship(back_populates="daily_standings")

# --- Supervisor / Agent Models ---

class AgentTask(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    task_type: str  # e.g., "calculate_roto", "import_roster"
    status: str = "pending" # pending, running, completed, failed
    payload: Dict = Field(default={}, sa_type=JSON)
    result: Dict = Field(default={}, sa_type=JSON)
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[str] = Field(default=None, foreign_key="agenttask.id")
    entity_type: str # "League", "Team"
    entity_id: int
    action: str # "update_roster", "calculate_standings"
    timestamp: datetime = Field(default_factory=utc_now)
    details: Dict = Field(default={}, sa_type=JSON)
