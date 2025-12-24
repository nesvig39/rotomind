from typing import Dict, List, Any
from sqlmodel import Session, select
from src.core.models import League, FantasyTeam, Player
import difflib

class RosterImporter:
    def __init__(self, session: Session):
        self.session = session
        self.players_cache = self._load_players()

    def _load_players(self):
        """Loads all active players into memory for matching."""
        players = self.session.exec(select(Player)).all()
        return {p.full_name.lower(): p for p in players}

    def find_player(self, name: str) -> Player:
        """Attempts to find a player by name (exact or fuzzy)."""
        name_clean = name.strip().lower()
        
        # 1. Exact Match
        if name_clean in self.players_cache:
            return self.players_cache[name_clean]
            
        # 2. Fuzzy Match
        matches = difflib.get_close_matches(name_clean, self.players_cache.keys(), n=1, cutoff=0.8)
        if matches:
            return self.players_cache[matches[0]]
            
        return None

    def process_import(self, league_id: int, roster_map: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Imports rosters.
        roster_map: {"Team Name": ["Player 1", "Player 2"]}
        """
        league = self.session.get(League, league_id)
        if not league:
            return {"error": "League not found"}
            
        report = {
            "teams_created": 0,
            "teams_updated": 0,
            "players_added": 0,
            "players_not_found": []
        }
        
        for team_name, player_names in roster_map.items():
            # Find or Create Team
            stmt = select(FantasyTeam).where(
                FantasyTeam.name == team_name,
                FantasyTeam.league_id == league_id
            )
            team = self.session.exec(stmt).first()
            
            if not team:
                team = FantasyTeam(name=team_name, league_id=league_id)
                self.session.add(team)
                report["teams_created"] += 1
            else:
                report["teams_updated"] += 1
                
            # We need to commit here to get team ID if created? 
            # Or just add to session and rely on relationship management
            # Adding team to session is enough for relationship appending if we are careful
            
            # Clear existing roster? For wizard, maybe we append?
            # Let's assume we append/ensure presence.
            
            for p_name in player_names:
                player = self.find_player(p_name)
                if player:
                    if player not in team.players:
                        team.players.append(player)
                        report["players_added"] += 1
                else:
                    report["players_not_found"].append({"team": team_name, "player": p_name})
                    
            self.session.add(team)
            
        self.session.commit()
        return report
