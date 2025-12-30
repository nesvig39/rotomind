"""
ESPN Fantasy Basketball Client

Scrapes data from a specific ESPN Fantasy Basketball league.

IMPORTANT LEGAL NOTICE:
- Screen scraping may violate ESPN's Terms of Service
- Use at your own risk for personal/educational purposes only
- Consider using ESPN's official Fantasy API if available
- Rate limit requests to avoid being blocked

This module demonstrates the technical approach but should be used responsibly.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging
import time
import json
import re

logger = logging.getLogger(__name__)


@dataclass
class ESPNSyncResult:
    """Result of an ESPN sync operation."""
    success: bool
    teams_synced: int = 0
    players_synced: int = 0
    stats_synced: int = 0
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "teams_synced": self.teams_synced,
            "players_synced": self.players_synced,
            "stats_synced": self.stats_synced,
            "errors": self.errors,
        }


@dataclass
class ESPNPlayer:
    """ESPN player data structure."""
    espn_id: int
    name: str
    team: str
    position: str
    fantasy_team_id: Optional[int] = None
    fantasy_team_name: Optional[str] = None
    is_free_agent: bool = False
    # Stats
    pts: float = 0.0
    reb: float = 0.0
    ast: float = 0.0
    stl: float = 0.0
    blk: float = 0.0
    fg_pct: float = 0.0
    ft_pct: float = 0.0
    tpm: float = 0.0
    tov: float = 0.0
    # Projections (ESPN provides these)
    projected_pts: float = 0.0
    projected_reb: float = 0.0
    projected_ast: float = 0.0


class ESPNFantasyClient:
    """
    Client for scraping ESPN Fantasy Basketball league data.
    
    USAGE:
        client = ESPNFantasyClient(
            league_id=12345678,
            season=2025,
            espn_s2="your_espn_s2_cookie",
            swid="your_swid_cookie"
        )
        
    To get cookies:
        1. Log into ESPN Fantasy
        2. Open browser developer tools (F12)
        3. Go to Application > Cookies
        4. Copy 'espn_s2' and 'SWID' values
        
    IMPORTANT: The espn_s2 cookie should be URL-encoded (keep the %2B etc.)
    """
    
    # Use lm-api-reads endpoint which works reliably
    BASE_URL = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/fba/seasons/{season}/segments/0/leagues/{league_id}"
    
    # Rate limiting
    MIN_REQUEST_INTERVAL = 2.0  # Be respectful to ESPN's servers
    
    def __init__(
        self, 
        league_id: int,
        season: int = 2026,  # 2025-26 NBA season uses 2026
        espn_s2: Optional[str] = None,
        swid: Optional[str] = None
    ):
        self.league_id = league_id
        self.season = season
        self.espn_s2 = espn_s2
        self.swid = swid
        self._last_request_time = 0
        
        # Session for maintaining cookies
        self.session = requests.Session()
        if espn_s2 and swid:
            self.session.cookies.set("espn_s2", espn_s2)
            self.session.cookies.set("SWID", swid)
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'Accept': 'application/json',
        })
    
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.MIN_REQUEST_INTERVAL:
            time.sleep(self.MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.time()
    
    def _get_api_url(self, view: Optional[str] = None) -> str:
        """Build API URL with optional view parameter."""
        url = self.BASE_URL.format(season=self.season, league_id=self.league_id)
        if view:
            url += f"?view={view}"
        return url
    
    def fetch_league_info(self) -> Optional[Dict]:
        """Fetch basic league information."""
        self._rate_limit()
        try:
            url = self._get_api_url()
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 401:
                logger.error("Authentication required. Provide espn_s2 and swid cookies.")
                return None
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch league info: {e}")
            return None
    
    def fetch_teams(self) -> List[Dict]:
        """Fetch all teams in the league with their rosters."""
        self._rate_limit()
        try:
            # Use mTeam view to get team data with rosters
            url = self._get_api_url("mTeam")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            teams = data.get("teams", [])
            
            result = []
            for team in teams:
                team_data = {
                    "id": team.get("id"),
                    "name": team.get("name", team.get("nickname", f"Team {team.get('id')}")),
                    "owner": team.get("owners", [{}])[0].get("firstName", "Unknown"),
                    "roster": []
                }
                
                # Extract roster
                roster = team.get("roster", {}).get("entries", [])
                for entry in roster:
                    player_info = entry.get("playerPoolEntry", {}).get("player", {})
                    if player_info:
                        team_data["roster"].append({
                            "espn_id": player_info.get("id"),
                            "name": player_info.get("fullName"),
                            "position": self._decode_position(player_info.get("defaultPositionId")),
                            "team": self._decode_nba_team(player_info.get("proTeamId")),
                        })
                
                result.append(team_data)
            
            logger.info(f"Fetched {len(result)} teams from ESPN league")
            return result
            
        except Exception as e:
            logger.error(f"Failed to fetch teams: {e}")
            return []
    
    def fetch_player_stats(self, scoring_period_id: Optional[int] = None) -> List[ESPNPlayer]:
        """
        Fetch player statistics.
        
        Args:
            scoring_period_id: Specific day to fetch (None = season totals)
        """
        self._rate_limit()
        try:
            # Use kona_player_info view for detailed player stats
            url = self._get_api_url("kona_player_info")
            
            # Add filters for player stats
            headers = {
                "x-fantasy-filter": json.dumps({
                    "players": {
                        "filterSlotIds": {"value": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]},
                        "limit": 500,
                        "sortPercOwned": {"sortPriority": 1, "sortAsc": False},
                    }
                })
            }
            
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            players_data = data.get("players", [])
            
            players = []
            for p in players_data:
                player_info = p.get("player", {})
                stats = self._extract_stats(player_info.get("stats", []))
                
                players.append(ESPNPlayer(
                    espn_id=player_info.get("id"),
                    name=player_info.get("fullName", "Unknown"),
                    team=self._decode_nba_team(player_info.get("proTeamId")),
                    position=self._decode_position(player_info.get("defaultPositionId")),
                    pts=stats.get("pts", 0),
                    reb=stats.get("reb", 0),
                    ast=stats.get("ast", 0),
                    stl=stats.get("stl", 0),
                    blk=stats.get("blk", 0),
                    tpm=stats.get("tpm", 0),
                    fg_pct=stats.get("fg_pct", 0),
                    ft_pct=stats.get("ft_pct", 0),
                    tov=stats.get("tov", 0),
                ))
            
            logger.info(f"Fetched stats for {len(players)} players")
            return players
            
        except Exception as e:
            logger.error(f"Failed to fetch player stats: {e}")
            return []
    
    def fetch_free_agents(self, limit: int = 50) -> List[ESPNPlayer]:
        """Fetch available free agents."""
        self._rate_limit()
        try:
            url = self._get_api_url("kona_player_info")
            
            headers = {
                "x-fantasy-filter": json.dumps({
                    "players": {
                        "filterStatus": {"value": ["FREEAGENT", "WAIVERS"]},
                        "limit": limit,
                        "sortPercOwned": {"sortPriority": 1, "sortAsc": False},
                    }
                })
            }
            
            response = self.session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            players = []
            
            for p in data.get("players", []):
                player_info = p.get("player", {})
                stats = self._extract_stats(player_info.get("stats", []))
                
                player = ESPNPlayer(
                    espn_id=player_info.get("id"),
                    name=player_info.get("fullName", "Unknown"),
                    team=self._decode_nba_team(player_info.get("proTeamId")),
                    position=self._decode_position(player_info.get("defaultPositionId")),
                    is_free_agent=True,
                    pts=stats.get("pts", 0),
                    reb=stats.get("reb", 0),
                    ast=stats.get("ast", 0),
                )
                players.append(player)
            
            logger.info(f"Fetched {len(players)} free agents")
            return players
            
        except Exception as e:
            logger.error(f"Failed to fetch free agents: {e}")
            return []
    
    def fetch_matchups(self, matchup_period: Optional[int] = None) -> List[Dict]:
        """Fetch current matchups/scores."""
        self._rate_limit()
        try:
            url = self._get_api_url("mMatchup")
            if matchup_period:
                url += f"&scoringPeriodId={matchup_period}"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            schedule = data.get("schedule", [])
            
            matchups = []
            for match in schedule:
                if match.get("matchupPeriodId") == matchup_period or matchup_period is None:
                    matchups.append({
                        "home_team_id": match.get("home", {}).get("teamId"),
                        "away_team_id": match.get("away", {}).get("teamId"),
                        "home_score": match.get("home", {}).get("totalPoints", 0),
                        "away_score": match.get("away", {}).get("totalPoints", 0),
                    })
            
            return matchups
            
        except Exception as e:
            logger.error(f"Failed to fetch matchups: {e}")
            return []
    
    def _extract_stats(self, stats_list: List[Dict]) -> Dict[str, float]:
        """Extract stats from ESPN's nested stats structure."""
        result = {}
        
        # ESPN stat IDs (these are consistent across their API)
        STAT_MAP = {
            0: "pts",
            1: "blk",
            2: "stl", 
            3: "ast",
            6: "reb",
            17: "tpm",
            19: "fg_pct",
            20: "ft_pct",
            11: "tov",
        }
        
        for stat_set in stats_list:
            if stat_set.get("statSourceId") == 0:  # Actual stats (not projections)
                stats = stat_set.get("stats", {})
                for stat_id, stat_name in STAT_MAP.items():
                    if str(stat_id) in stats:
                        result[stat_name] = stats[str(stat_id)]
        
        return result
    
    def _decode_position(self, position_id: int) -> str:
        """Decode ESPN position ID to string."""
        positions = {1: "PG", 2: "SG", 3: "SF", 4: "PF", 5: "C"}
        return positions.get(position_id, "UTIL")
    
    def _decode_nba_team(self, team_id: int) -> str:
        """Decode ESPN team ID to abbreviation."""
        teams = {
            1: "ATL", 2: "BOS", 3: "BKN", 4: "CHA", 5: "CHI",
            6: "CLE", 7: "DAL", 8: "DEN", 9: "DET", 10: "GSW",
            11: "HOU", 12: "IND", 13: "LAC", 14: "LAL", 15: "MEM",
            16: "MIA", 17: "MIL", 18: "MIN", 19: "NOP", 20: "NYK",
            21: "OKC", 22: "ORL", 23: "PHI", 24: "PHO", 25: "POR",
            26: "SAC", 27: "SAS", 28: "TOR", 29: "UTA", 30: "WAS",
        }
        return teams.get(team_id, "FA")


class ESPNRosterImporter:
    """
    Imports rosters directly from ESPN Fantasy Basketball.
    
    Benefits over manual import:
    - No fuzzy matching needed (direct ESPN player IDs)
    - Automatic roster updates
    - Includes waiver/trade transaction history
    """
    
    def __init__(self, espn_client: ESPNFantasyClient, db_session):
        self.espn_client = espn_client
        self.session = db_session
        self._espn_to_nba_id_map: Optional[Dict[int, int]] = None
    
    def build_id_mapping(self) -> Dict[int, int]:
        """
        Build mapping from ESPN player IDs to NBA player IDs.
        
        This is needed because ESPN uses different IDs than NBA.com.
        The mapping can be built by matching player names.
        """
        if self._espn_to_nba_id_map:
            return self._espn_to_nba_id_map
        
        from src.core.models import Player
        from sqlmodel import select
        
        # Get all NBA players from database
        nba_players = self.session.exec(select(Player)).all()
        nba_by_name = {p.full_name.lower(): p.nba_id for p in nba_players}
        
        # Get ESPN players
        espn_players = self.espn_client.fetch_player_stats()
        
        mapping = {}
        for ep in espn_players:
            name_lower = ep.name.lower()
            if name_lower in nba_by_name:
                mapping[ep.espn_id] = nba_by_name[name_lower]
        
        self._espn_to_nba_id_map = mapping
        logger.info(f"Built ESPN->NBA ID mapping for {len(mapping)} players")
        return mapping
    
    def sync_league_rosters(self, local_league_id: int) -> ESPNSyncResult:
        """
        Sync all rosters from ESPN to local database.
        
        Args:
            local_league_id: The ID of the league in our database
        """
        from src.core.models import League, FantasyTeam, Player
        from sqlmodel import select
        
        result = ESPNSyncResult(success=False)
        
        try:
            # Verify local league exists
            league = self.session.get(League, local_league_id)
            if not league:
                result.errors.append(f"Local league {local_league_id} not found")
                return result
            
            # Build ID mapping
            id_map = self.build_id_mapping()
            
            # Fetch ESPN teams
            espn_teams = self.espn_client.fetch_teams()
            
            for espn_team in espn_teams:
                # Find or create local team
                stmt = select(FantasyTeam).where(
                    FantasyTeam.name == espn_team["name"],
                    FantasyTeam.league_id == local_league_id
                )
                local_team = self.session.exec(stmt).first()
                
                if not local_team:
                    local_team = FantasyTeam(
                        name=espn_team["name"],
                        owner_name=espn_team.get("owner"),
                        league_id=local_league_id
                    )
                    self.session.add(local_team)
                    self.session.flush()
                
                # Clear existing roster and rebuild
                local_team.players.clear()
                
                # Add players from ESPN roster
                for espn_player in espn_team.get("roster", []):
                    espn_id = espn_player.get("espn_id")
                    
                    if espn_id in id_map:
                        nba_id = id_map[espn_id]
                        # Find player by NBA ID
                        stmt = select(Player).where(Player.nba_id == nba_id)
                        player = self.session.exec(stmt).first()
                        
                        if player:
                            local_team.players.append(player)
                            result.players_synced += 1
                    else:
                        result.errors.append(
                            f"No NBA ID mapping for ESPN player: {espn_player.get('name')}"
                        )
                
                result.teams_synced += 1
            
            self.session.commit()
            result.success = True
            logger.info(
                f"Synced {result.teams_synced} teams, {result.players_synced} players"
            )
            
        except Exception as e:
            self.session.rollback()
            result.errors.append(str(e))
            logger.error(f"ESPN roster sync failed: {e}")
        
        return result
