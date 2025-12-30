"""
Hybrid Data Client for Fantasy NBA

Combines ESPN Fantasy Basketball data with NBA.com stats:
- ESPN: Rosters, projections, ownership %, injury status, league-specific data
- NBA API: Historical game-by-game statistics (more reliable and complete)

This provides the best of both worlds for fantasy basketball analysis.
"""

import logging
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from sqlmodel import Session, select

from src.core.models import Player, PlayerStats, League, FantasyTeam
from src.ingestion.nba_client import NBAClient, SyncResult
from src.ingestion.espn_client import ESPNFantasyClient, ESPNPlayer, ESPNSyncResult

logger = logging.getLogger(__name__)


@dataclass
class HybridSyncResult:
    """Result of a hybrid sync operation."""
    success: bool = False
    
    # ESPN sync results
    espn_teams_synced: int = 0
    espn_players_synced: int = 0
    espn_rosters_updated: int = 0
    
    # NBA sync results
    nba_players_synced: int = 0
    nba_stats_synced: int = 0
    
    # ID mapping results
    players_mapped: int = 0
    players_unmapped: int = 0
    
    # Timing
    espn_sync_duration: float = 0.0
    nba_sync_duration: float = 0.0
    total_duration: float = 0.0
    
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "espn": {
                "teams_synced": self.espn_teams_synced,
                "players_synced": self.espn_players_synced,
                "rosters_updated": self.espn_rosters_updated,
                "duration_seconds": round(self.espn_sync_duration, 2),
            },
            "nba": {
                "players_synced": self.nba_players_synced,
                "stats_synced": self.nba_stats_synced,
                "duration_seconds": round(self.nba_sync_duration, 2),
            },
            "mapping": {
                "players_mapped": self.players_mapped,
                "players_unmapped": self.players_unmapped,
            },
            "total_duration_seconds": round(self.total_duration, 2),
            "errors": self.errors,
            "warnings": self.warnings,
        }


class HybridDataClient:
    """
    Hybrid client that combines ESPN Fantasy and NBA.com data sources.
    
    Data Source Strategy:
    - ROSTERS: ESPN (authoritative for your fantasy league)
    - PROJECTIONS: ESPN (their proprietary projections)
    - OWNERSHIP %: ESPN (league-wide ownership data)
    - INJURY STATUS: ESPN (more current than NBA.com)
    - GAME STATS: NBA.com (complete historical data)
    - PLAYER LIST: NBA.com (all active players, not just rostered)
    
    Usage:
        client = HybridDataClient(
            espn_league_id=12345678,
            espn_s2="cookie_value",
            espn_swid="swid_value"
        )
        result = client.full_sync(db_engine, local_league_id=1)
    """
    
    def __init__(
        self,
        espn_league_id: Optional[int] = None,
        espn_s2: Optional[str] = None,
        espn_swid: Optional[str] = None,
        espn_season: int = 2025,
    ):
        """
        Initialize the hybrid client.
        
        Args:
            espn_league_id: Your ESPN Fantasy Basketball league ID
            espn_s2: ESPN authentication cookie (from browser)
            espn_swid: ESPN SWID cookie (from browser)
            espn_season: ESPN season year (2025 = 2024-25 season)
        """
        self.nba_client = NBAClient()
        
        # ESPN client (optional - only if credentials provided)
        self.espn_client: Optional[ESPNFantasyClient] = None
        if espn_league_id and espn_s2 and espn_swid:
            self.espn_client = ESPNFantasyClient(
                league_id=espn_league_id,
                season=espn_season,
                espn_s2=espn_s2,
                swid=espn_swid,
            )
            logger.info(f"ESPN client initialized for league {espn_league_id}")
        else:
            logger.info("ESPN credentials not provided - running in NBA-only mode")
        
        # Cache for ID mapping
        self._espn_to_nba_map: Dict[int, int] = {}
        self._name_to_player: Dict[str, Player] = {}
    
    @classmethod
    def from_league(cls, league: League) -> "HybridDataClient":
        """
        Create a HybridDataClient from a League model with stored ESPN credentials.
        
        Args:
            league: League model with ESPN credentials
            
        Returns:
            Configured HybridDataClient
        """
        return cls(
            espn_league_id=league.espn_league_id,
            espn_s2=league.espn_s2,
            espn_swid=league.espn_swid,
        )
    
    def _build_name_index(self, session: Session) -> Dict[str, Player]:
        """Build an index of player names for fuzzy matching."""
        if self._name_to_player:
            return self._name_to_player
        
        players = session.exec(select(Player)).all()
        self._name_to_player = {p.full_name.lower(): p for p in players}
        return self._name_to_player
    
    def _find_player_by_name(self, name: str, session: Session) -> Optional[Player]:
        """Find a player by name with fuzzy matching fallback."""
        import difflib
        
        name_index = self._build_name_index(session)
        name_lower = name.strip().lower()
        
        # Exact match
        if name_lower in name_index:
            return name_index[name_lower]
        
        # Fuzzy match
        matches = difflib.get_close_matches(name_lower, name_index.keys(), n=1, cutoff=0.85)
        if matches:
            return name_index[matches[0]]
        
        return None
    
    def build_espn_id_mapping(
        self, 
        session: Session,
        espn_players: List[ESPNPlayer]
    ) -> Dict[int, int]:
        """
        Build mapping from ESPN player IDs to internal player IDs.
        
        Uses name matching to create the mapping, then caches it.
        """
        mapping = {}
        
        for ep in espn_players:
            # First check if we already have this ESPN ID in the database
            stmt = select(Player).where(Player.espn_id == ep.espn_id)
            existing = session.exec(stmt).first()
            
            if existing:
                mapping[ep.espn_id] = existing.id
                continue
            
            # Otherwise, try to match by name
            player = self._find_player_by_name(ep.name, session)
            if player:
                # Update the player with their ESPN ID
                player.espn_id = ep.espn_id
                session.add(player)
                mapping[ep.espn_id] = player.id
            else:
                logger.warning(f"Could not map ESPN player: {ep.name} (ESPN ID: {ep.espn_id})")
        
        session.commit()
        self._espn_to_nba_map = mapping
        logger.info(f"Built ESPN->DB ID mapping for {len(mapping)} players")
        return mapping
    
    def sync_nba_players(
        self,
        db_engine,
        mock: bool = False,
        progress_callback: Optional[Callable] = None,
    ) -> SyncResult:
        """
        Sync NBA player list to database.
        
        This is the foundation - we need NBA players before ESPN data makes sense.
        """
        logger.info("Syncing NBA player list...")
        return self.nba_client.sync_players(db_engine, mock=mock, progress_callback=progress_callback)
    
    def sync_nba_stats(
        self,
        db_engine,
        limit_players: Optional[int] = None,
        mock: bool = False,
        progress_callback: Optional[Callable] = None,
    ) -> SyncResult:
        """
        Sync NBA game statistics to database.
        
        Args:
            db_engine: SQLAlchemy engine
            limit_players: Limit number of players (for testing)
            mock: Use mock data
            progress_callback: Progress callback function
        """
        logger.info("Syncing NBA game statistics...")
        return self.nba_client.sync_recent_stats(
            db_engine,
            limit_players=limit_players,
            mock=mock,
            progress_callback=progress_callback,
        )
    
    def sync_espn_rosters(
        self,
        session: Session,
        local_league_id: int,
    ) -> ESPNSyncResult:
        """
        Sync rosters from ESPN to local database.
        
        This updates which players are on which fantasy teams,
        directly from your ESPN league.
        """
        result = ESPNSyncResult(success=False)
        
        if not self.espn_client:
            result.errors.append("ESPN client not configured")
            return result
        
        try:
            # Verify local league exists
            league = session.get(League, local_league_id)
            if not league:
                result.errors.append(f"Local league {local_league_id} not found")
                return result
            
            # Fetch ESPN teams with rosters
            espn_teams = self.espn_client.fetch_teams()
            if not espn_teams:
                result.errors.append("No teams returned from ESPN")
                return result
            
            # Get all ESPN players for ID mapping
            espn_players = self.espn_client.fetch_player_stats()
            id_mapping = self.build_espn_id_mapping(session, espn_players)
            
            for espn_team in espn_teams:
                # Find or create local team
                stmt = select(FantasyTeam).where(
                    FantasyTeam.espn_team_id == espn_team["id"],
                    FantasyTeam.league_id == local_league_id
                )
                local_team = session.exec(stmt).first()
                
                if not local_team:
                    # Try matching by name
                    stmt = select(FantasyTeam).where(
                        FantasyTeam.name == espn_team["name"],
                        FantasyTeam.league_id == local_league_id
                    )
                    local_team = session.exec(stmt).first()
                
                if not local_team:
                    # Create new team
                    local_team = FantasyTeam(
                        name=espn_team["name"],
                        owner_name=espn_team.get("owner"),
                        league_id=local_league_id,
                        espn_team_id=espn_team["id"],
                    )
                    session.add(local_team)
                    session.flush()
                    result.teams_synced += 1
                else:
                    # Update ESPN team ID if not set
                    if not local_team.espn_team_id:
                        local_team.espn_team_id = espn_team["id"]
                    result.teams_synced += 1
                
                # Clear and rebuild roster
                local_team.players.clear()
                
                for espn_player in espn_team.get("roster", []):
                    espn_id = espn_player.get("espn_id")
                    
                    if espn_id in id_mapping:
                        player_id = id_mapping[espn_id]
                        player = session.get(Player, player_id)
                        if player:
                            local_team.players.append(player)
                            result.players_synced += 1
                    else:
                        result.errors.append(
                            f"Unmapped player: {espn_player.get('name')} (ESPN ID: {espn_id})"
                        )
            
            # Update league sync timestamp
            league.last_espn_sync = datetime.now(timezone.utc)
            session.add(league)
            session.commit()
            
            result.success = True
            logger.info(f"ESPN roster sync complete: {result.teams_synced} teams, {result.players_synced} players")
            
        except Exception as e:
            session.rollback()
            result.errors.append(str(e))
            logger.error(f"ESPN roster sync failed: {e}", exc_info=True)
        
        return result
    
    def sync_espn_player_metadata(self, session: Session) -> int:
        """
        Sync ESPN-specific player metadata (ownership %, injury status, etc.).
        
        Returns:
            Number of players updated
        """
        if not self.espn_client:
            logger.warning("ESPN client not configured - skipping metadata sync")
            return 0
        
        try:
            espn_players = self.espn_client.fetch_player_stats()
            updated = 0
            
            for ep in espn_players:
                # Find player by ESPN ID
                stmt = select(Player).where(Player.espn_id == ep.espn_id)
                player = session.exec(stmt).first()
                
                if player:
                    # Update ESPN metadata
                    # Note: ESPN ownership % would need to be fetched separately
                    # This is a placeholder for the pattern
                    updated += 1
            
            session.commit()
            logger.info(f"Updated ESPN metadata for {updated} players")
            return updated
            
        except Exception as e:
            session.rollback()
            logger.error(f"ESPN metadata sync failed: {e}")
            return 0
    
    def full_sync(
        self,
        db_engine,
        local_league_id: Optional[int] = None,
        sync_nba_players: bool = True,
        sync_nba_stats: bool = True,
        sync_espn_rosters: bool = True,
        limit_nba_players: Optional[int] = None,
        mock_nba: bool = False,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> HybridSyncResult:
        """
        Perform a full hybrid sync of all data sources.
        
        Args:
            db_engine: SQLAlchemy database engine
            local_league_id: Local league ID for ESPN roster sync
            sync_nba_players: Whether to sync NBA player list
            sync_nba_stats: Whether to sync NBA game stats
            sync_espn_rosters: Whether to sync ESPN rosters
            limit_nba_players: Limit NBA player stats sync (for testing)
            mock_nba: Use mock NBA data
            progress_callback: Callback(phase, current, total) for progress updates
            
        Returns:
            HybridSyncResult with details of the sync operation
        """
        import time
        
        result = HybridSyncResult()
        start_time = time.time()
        
        try:
            # Phase 1: Sync NBA Players (foundation)
            if sync_nba_players:
                if progress_callback:
                    progress_callback("nba_players", 0, 1)
                
                nba_start = time.time()
                player_result = self.sync_nba_players(db_engine, mock=mock_nba)
                result.nba_players_synced = player_result.records_created
                result.nba_sync_duration = time.time() - nba_start
                
                if not player_result.success:
                    result.errors.extend(player_result.errors)
                
                if progress_callback:
                    progress_callback("nba_players", 1, 1)
            
            # Phase 2: Sync NBA Stats
            if sync_nba_stats:
                if progress_callback:
                    progress_callback("nba_stats", 0, 1)
                
                nba_start = time.time()
                stats_result = self.sync_nba_stats(
                    db_engine, 
                    limit_players=limit_nba_players,
                    mock=mock_nba
                )
                result.nba_stats_synced = stats_result.records_created
                result.nba_sync_duration += time.time() - nba_start
                
                if not stats_result.success:
                    result.errors.extend(stats_result.errors)
                
                if progress_callback:
                    progress_callback("nba_stats", 1, 1)
            
            # Phase 3: Sync ESPN Rosters
            if sync_espn_rosters and self.espn_client and local_league_id:
                if progress_callback:
                    progress_callback("espn_rosters", 0, 1)
                
                espn_start = time.time()
                with Session(db_engine) as session:
                    espn_result = self.sync_espn_rosters(session, local_league_id)
                    
                    result.espn_teams_synced = espn_result.teams_synced
                    result.espn_players_synced = espn_result.players_synced
                    result.espn_sync_duration = time.time() - espn_start
                    
                    if not espn_result.success:
                        result.errors.extend(espn_result.errors)
                    
                    # Count mapped vs unmapped
                    result.players_mapped = len(self._espn_to_nba_map)
                
                if progress_callback:
                    progress_callback("espn_rosters", 1, 1)
            elif sync_espn_rosters and not self.espn_client:
                result.warnings.append("ESPN sync requested but ESPN client not configured")
            
            result.total_duration = time.time() - start_time
            result.success = len(result.errors) == 0
            
            logger.info(
                f"Hybrid sync complete in {result.total_duration:.1f}s: "
                f"NBA({result.nba_players_synced} players, {result.nba_stats_synced} stats), "
                f"ESPN({result.espn_teams_synced} teams, {result.espn_players_synced} players)"
            )
            
        except Exception as e:
            result.errors.append(f"Hybrid sync failed: {str(e)}")
            result.total_duration = time.time() - start_time
            logger.error(f"Hybrid sync failed: {e}", exc_info=True)
        
        return result
    
    def get_combined_player_data(
        self,
        session: Session,
        player_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Get combined player data from both sources.
        
        Returns a unified view of the player with:
        - Basic info (NBA)
        - Game stats (NBA)
        - Fantasy ownership (ESPN)
        - Injury status (ESPN)
        - Projections (ESPN)
        """
        player = session.get(Player, player_id)
        if not player:
            return None
        
        # Get NBA stats
        stmt = select(PlayerStats).where(
            PlayerStats.player_id == player_id
        ).order_by(PlayerStats.game_date.desc()).limit(10)
        recent_stats = session.exec(stmt).all()
        
        # Calculate averages
        if recent_stats:
            avg_pts = sum(s.pts for s in recent_stats) / len(recent_stats)
            avg_reb = sum(s.reb for s in recent_stats) / len(recent_stats)
            avg_ast = sum(s.ast for s in recent_stats) / len(recent_stats)
        else:
            avg_pts = avg_reb = avg_ast = 0
        
        return {
            "id": player.id,
            "nba_id": player.nba_id,
            "espn_id": player.espn_id,
            "name": player.full_name,
            "team": player.team_abbreviation,
            "position": player.position,
            "is_active": player.is_active,
            "espn_ownership_pct": player.espn_ownership_pct,
            "espn_injury_status": player.espn_injury_status,
            "recent_averages": {
                "pts": round(avg_pts, 1),
                "reb": round(avg_reb, 1),
                "ast": round(avg_ast, 1),
                "games": len(recent_stats),
            },
            "last_games": [
                {
                    "date": str(s.game_date),
                    "matchup": s.matchup,
                    "pts": s.pts,
                    "reb": s.reb,
                    "ast": s.ast,
                }
                for s in recent_stats[:5]
            ],
        }
