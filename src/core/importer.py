from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from sqlmodel import Session, select
from src.core.models import League, FantasyTeam, Player
import difflib
import logging

logger = logging.getLogger(__name__)


class ImportError(Exception):
    """Raised when roster import fails."""
    pass


@dataclass
class ImportReport:
    """Detailed report of an import operation."""
    success: bool = True
    teams_created: int = 0
    teams_updated: int = 0
    players_added: int = 0
    players_not_found: List[Dict[str, str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "teams_created": self.teams_created,
            "teams_updated": self.teams_updated,
            "players_added": self.players_added,
            "players_not_found": self.players_not_found,
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
