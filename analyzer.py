import pandas as pd
from stats import calculate_z_scores, aggregate_player_stats

class TradeAnalyzer:
    def __init__(self, all_player_stats: pd.DataFrame):
        """
        all_player_stats: DataFrame containing averaged stats for all players in the league.
                          Must include Z-scores.
        """
        self.stats = all_player_stats

    def analyze_trade(self, team_a_roster: list, team_b_roster: list, 
                      players_to_b: list, players_to_a: list):
        """
        Analyzes the impact of a trade between Team A and Team B.
        team_a_roster: List of player_ids currently on Team A.
        team_b_roster: List of player_ids currently on Team B.
        players_to_b: List of player_ids moving from A to B.
        players_to_a: List of player_ids moving from B to A.
        """
        
        # Current State
        team_a_current = self._calculate_team_score(team_a_roster)
        team_b_current = self._calculate_team_score(team_b_roster)
        
        # New Rosters
        new_roster_a = [p for p in team_a_roster if p not in players_to_b] + players_to_a
        new_roster_b = [p for p in team_b_roster if p not in players_to_a] + players_to_b
        
        # Future State
        team_a_new = self._calculate_team_score(new_roster_a)
        team_b_new = self._calculate_team_score(new_roster_b)
        
        return {
            "team_a": {
                "before": team_a_current,
                "after": team_a_new,
                "diff": team_a_new['total_z'] - team_a_current['total_z']
            },
            "team_b": {
                "before": team_b_current,
                "after": team_b_new,
                "diff": team_b_new['total_z'] - team_b_current['total_z']
            }
        }
        
    def _calculate_team_score(self, roster_ids):
        """Calculates the aggregate Z-score for a list of players."""
        team_stats = self.stats[self.stats['player_id'].isin(roster_ids)]
        if team_stats.empty:
            return {'total_z': 0}
            
        # Summing z-scores for the team is a proxy for roto strength
        # In real roto, you sum raw stats then rank, but Sum of Z is a good approximation for trade value
        return {
            'total_z': team_stats['z_total'].sum(),
            'avg_z': team_stats['z_total'].mean(),
            'categories': team_stats[['z_PTS', 'z_REB', 'z_AST', 'z_STL', 'z_BLK', 'z_FG3M', 'z_FG_PCT', 'z_FT_PCT']].sum().to_dict()
        }
