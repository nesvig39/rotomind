from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import date

# Link table for Many-to-Many relationship
class TeamRoster(SQLModel, table=True):
    team_id: Optional[int] = Field(default=None, foreign_key="fantasyteam.id", primary_key=True)
    player_id: Optional[int] = Field(default=None, foreign_key="player.id", primary_key=True)

class League(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    season: str = "2024-25"
    
    teams: List["FantasyTeam"] = Relationship(back_populates="league")

class Player(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    nba_id: int = Field(unique=True, index=True)
    full_name: str
    team_abbreviation: Optional[str] = None
    position: Optional[str] = None
    is_active: bool = True
    
    stats: List["PlayerStats"] = Relationship(back_populates="player")
    teams: List["FantasyTeam"] = Relationship(back_populates="players", link_model=TeamRoster)

class PlayerStats(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="player.id")
    game_date: date
    game_id: str
    matchup: str
    pts: int = 0
    reb: int = 0
    ast: int = 0
    stl: int = 0
    blk: int = 0
    fgm: int = 0
    fga: int = 0
    ftm: int = 0
    fta: int = 0
    tpm: int = 0
    tov: int = 0
    
    player: Player = Relationship(back_populates="stats")

class FantasyTeam(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    owner_name: Optional[str] = None
    league_id: Optional[int] = Field(default=None, foreign_key="league.id")
    
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
