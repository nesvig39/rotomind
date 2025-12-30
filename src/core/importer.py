from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from sqlmodel import Session, select
from src.core.models import League, FantasyTeam, Player
import difflib
import logging

logger = logging.getLogger(__name__)


class ImportSource(Enum):
    """Source of roster import data."""
    MANUAL = "manual"  # JSON/manual input with fuzzy matching
    ESPN = "espn"      # Direct ESPN API with ID matching
    CSV = "csv"        # CSV file import


class ImportError(Exception):
    """Raised when roster import fails."""
    pass


@dataclass
class ImportReport:
    """Detailed report of an import operation."""
    success: bool = True
    source: str = "manual"
    teams_created: int = 0
    teams_updated: int = 0
    players_added: int = 0
    players_removed: int = 0
    players_not_found: List[Dict[str, str]] = field(default_factory=list)
    players_mapped: int = 0  # For ESPN: successfully mapped ESPN->NBA IDs
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "source": self.source,
            "teams_created": self.teams_created,
            "teams_updated": self.teams_updated,
            "players_added": self.players_added,
            "players_removed": self.players_removed,
            "players_not_found": self.players_not_found,
            "players_mapped": self.players_mapped,
            "warnings": self.warnings,
        }


class RosterImporter:
    """Imports fantasy rosters with fuzzy player name matching."""
    
    # Configurable matching threshold (0.0 to 1.0)
    FUZZY_MATCH_CUTOFF = 0.8
    
    def __init__(self, session: Session):
        self.session = session
        self._players_cache: Optional[Dict[str, Player]] = None

    @property
    def players_cache(self) -> Dict[str, Player]:
        """Lazy-load players cache on first access."""
        if self._players_cache is None:
            self._players_cache = self._load_players()
        return self._players_cache

    def _load_players(self) -> Dict[str, Player]:
        """Loads all active players into memory for matching."""
        players = self.session.exec(
            select(Player).where(Player.is_active == True)
        ).all()
        cache = {p.full_name.lower(): p for p in players}
        logger.debug(f"Loaded {len(cache)} players into matching cache")
        return cache

    def find_player(self, name: str) -> Optional[Player]:
        """
        Attempts to find a player by name (exact or fuzzy).
        
        Args:
            name: Player name to search for
            
        Returns:
            Player if found, None otherwise
        """
        if not name or not name.strip():
            return None
            
        name_clean = name.strip().lower()
        
        # 1. Exact Match
        if name_clean in self.players_cache:
            logger.debug(f"Exact match found for '{name}'")
            return self.players_cache[name_clean]
        
        # 2. Fuzzy Match
        matches = difflib.get_close_matches(
            name_clean, 
            self.players_cache.keys(), 
            n=1, 
            cutoff=self.FUZZY_MATCH_CUTOFF
        )
        if matches:
            matched_name = matches[0]
            logger.debug(f"Fuzzy match: '{name}' -> '{matched_name}'")
            return self.players_cache[matched_name]
        
        logger.debug(f"No match found for '{name}'")
        return None

    def validate_roster_map(self, roster_map: Dict[str, List[str]]) -> List[str]:
        """
        Validate roster map structure.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if not roster_map:
            errors.append("Roster map is empty")
            return errors
        
        if not isinstance(roster_map, dict):
            errors.append("Roster map must be a dictionary")
            return errors
        
        for team_name, players in roster_map.items():
            if not team_name or not team_name.strip():
                errors.append("Team name cannot be empty")
            if not isinstance(players, list):
                errors.append(f"Players for team '{team_name}' must be a list")
            elif not players:
                errors.append(f"Team '{team_name}' has no players")
        
        return errors

    def process_import(
        self, 
        league_id: int, 
        roster_map: Dict[str, List[str]],
        clear_existing: bool = False
    ) -> ImportReport:
        """
        Imports rosters for a league with transaction safety.
        
        Args:
            league_id: Target league ID
            roster_map: Mapping of team names to player names
                        Example: {"Team Name": ["Player 1", "Player 2"]}
            clear_existing: If True, clear existing roster before import
            
        Returns:
            ImportReport with operation details
            
        Raises:
            ImportError: If league not found or validation fails
        """
        report = ImportReport()
        
        # Validate input
        validation_errors = self.validate_roster_map(roster_map)
        if validation_errors:
            raise ImportError(f"Invalid roster map: {validation_errors}")
        
        # Verify league exists
        league = self.session.get(League, league_id)
        if not league:
            raise ImportError(f"League with ID {league_id} not found")
        
        logger.info(f"Starting roster import for league '{league.name}' (ID: {league_id})")
        
        try:
            for team_name, player_names in roster_map.items():
                team_name = team_name.strip()
                
                # Find or Create Team
                stmt = select(FantasyTeam).where(
                    FantasyTeam.name == team_name,
                    FantasyTeam.league_id == league_id
                )
                team = self.session.exec(stmt).first()
                
                if not team:
                    team = FantasyTeam(name=team_name, league_id=league_id)
                    self.session.add(team)
                    # Flush to get ID for relationship management
                    self.session.flush()
                    report.teams_created += 1
                    logger.debug(f"Created team: {team_name}")
                else:
                    report.teams_updated += 1
                    if clear_existing:
                        team.players.clear()
                        logger.debug(f"Cleared existing roster for team: {team_name}")
                
                # Track existing roster for duplicate detection
                existing_player_ids = {p.id for p in team.players}
                
                for player_name in player_names:
                    if not player_name or not player_name.strip():
                        report.warnings.append(f"Skipping empty player name in team '{team_name}'")
                        continue
                    
                    player = self.find_player(player_name)
                    if player:
                        if player.id not in existing_player_ids:
                            team.players.append(player)
                            existing_player_ids.add(player.id)
                            report.players_added += 1
                        else:
                            report.warnings.append(
                                f"Player '{player.full_name}' already on team '{team_name}'"
                            )
                    else:
                        report.players_not_found.append({
                            "team": team_name, 
                            "player": player_name.strip()
                        })
                
                self.session.add(team)
            
            self.session.commit()
            logger.info(
                f"Import complete: {report.teams_created} teams created, "
                f"{report.players_added} players added, "
                f"{len(report.players_not_found)} not found"
            )
            
        except Exception as e:
            self.session.rollback()
            report.success = False
            logger.error(f"Import failed, rolled back: {e}")
            raise ImportError(f"Import failed: {e}") from e
        
        return report

    def find_player_by_espn_id(self, espn_id: int) -> Optional[Player]:
        """
        Find a player by their ESPN ID.
        
        Args:
            espn_id: ESPN player ID
            
        Returns:
            Player if found, None otherwise
        """
        stmt = select(Player).where(Player.espn_id == espn_id)
        return self.session.exec(stmt).first()

    def process_espn_import(
        self,
        league_id: int,
        espn_teams: List[Dict[str, Any]],
        clear_existing: bool = True,
    ) -> ImportReport:
        """
        Import rosters directly from ESPN data.
        
        This uses ESPN player IDs for direct matching (no fuzzy matching needed).
        Falls back to name matching if ESPN ID is not found.
        
        Args:
            league_id: Target league ID
            espn_teams: List of ESPN team data with rosters
                        Format: [{"id": 1, "name": "Team Name", "roster": [{"espn_id": 123, "name": "Player"}]}]
            clear_existing: If True, clear existing roster before import (default True for ESPN sync)
            
        Returns:
            ImportReport with operation details
        """
        report = ImportReport(source=ImportSource.ESPN.value)
        
        # Verify league exists
        league = self.session.get(League, league_id)
        if not league:
            raise ImportError(f"League with ID {league_id} not found")
        
        logger.info(f"Starting ESPN roster import for league '{league.name}' (ID: {league_id})")
        
        try:
            for espn_team in espn_teams:
                espn_team_id = espn_team.get("id")
                team_name = espn_team.get("name", f"Team {espn_team_id}")
                
                # Find team by ESPN ID first, then by name
                stmt = select(FantasyTeam).where(
                    FantasyTeam.espn_team_id == espn_team_id,
                    FantasyTeam.league_id == league_id
                )
                team = self.session.exec(stmt).first()
                
                if not team:
                    # Try by name
                    stmt = select(FantasyTeam).where(
                        FantasyTeam.name == team_name,
                        FantasyTeam.league_id == league_id
                    )
                    team = self.session.exec(stmt).first()
                
                if not team:
                    # Create new team
                    team = FantasyTeam(
                        name=team_name,
                        owner_name=espn_team.get("owner"),
                        league_id=league_id,
                        espn_team_id=espn_team_id,
                    )
                    self.session.add(team)
                    self.session.flush()
                    report.teams_created += 1
                    logger.debug(f"Created team: {team_name} (ESPN ID: {espn_team_id})")
                else:
                    report.teams_updated += 1
                    # Update ESPN team ID if not set
                    if not team.espn_team_id and espn_team_id:
                        team.espn_team_id = espn_team_id
                    
                    if clear_existing:
                        old_count = len(team.players)
                        team.players.clear()
                        report.players_removed += old_count
                        logger.debug(f"Cleared {old_count} players from team: {team_name}")
                
                # Import roster
                existing_player_ids = {p.id for p in team.players}
                
                for espn_player in espn_team.get("roster", []):
                    espn_player_id = espn_player.get("espn_id")
                    player_name = espn_player.get("name", "Unknown")
                    
                    player = None
                    
                    # Try ESPN ID first (preferred - no ambiguity)
                    if espn_player_id:
                        player = self.find_player_by_espn_id(espn_player_id)
                        if player:
                            report.players_mapped += 1
                    
                    # Fall back to name matching
                    if not player and player_name:
                        player = self.find_player(player_name)
                        if player and espn_player_id:
                            # Update player with ESPN ID for future syncs
                            player.espn_id = espn_player_id
                            self.session.add(player)
                            report.players_mapped += 1
                    
                    if player:
                        if player.id not in existing_player_ids:
                            team.players.append(player)
                            existing_player_ids.add(player.id)
                            report.players_added += 1
                        else:
                            report.warnings.append(
                                f"Player '{player.full_name}' already on team '{team_name}'"
                            )
                    else:
                        report.players_not_found.append({
                            "team": team_name,
                            "player": player_name,
                            "espn_id": espn_player_id,
                        })
                
                self.session.add(team)
            
            self.session.commit()
            logger.info(
                f"ESPN import complete: {report.teams_created} created, "
                f"{report.teams_updated} updated, {report.players_added} players added, "
                f"{report.players_mapped} mapped by ESPN ID"
            )
            
        except Exception as e:
            self.session.rollback()
            report.success = False
            logger.error(f"ESPN import failed, rolled back: {e}")
            raise ImportError(f"ESPN import failed: {e}") from e
        
        return report

    def process_csv_import(
        self,
        league_id: int,
        csv_content: str,
        team_column: str = "Team",
        player_column: str = "Player",
        clear_existing: bool = False,
    ) -> ImportReport:
        """
        Import rosters from CSV content.
        
        CSV format should have at least two columns:
        - Team name column
        - Player name column
        
        Args:
            league_id: Target league ID
            csv_content: CSV file content as string
            team_column: Name of the team column
            player_column: Name of the player column
            clear_existing: If True, clear existing roster before import
            
        Returns:
            ImportReport with operation details
        """
        import csv
        from io import StringIO
        
        report = ImportReport(source=ImportSource.CSV.value)
        
        try:
            reader = csv.DictReader(StringIO(csv_content))
            
            # Build roster map from CSV
            roster_map: Dict[str, List[str]] = {}
            
            for row in reader:
                team_name = row.get(team_column, "").strip()
                player_name = row.get(player_column, "").strip()
                
                if not team_name or not player_name:
                    report.warnings.append(f"Skipping row with missing team/player: {row}")
                    continue
                
                if team_name not in roster_map:
                    roster_map[team_name] = []
                roster_map[team_name].append(player_name)
            
            # Use the standard import process
            return self.process_import(league_id, roster_map, clear_existing)
            
        except csv.Error as e:
            raise ImportError(f"CSV parsing failed: {e}")
