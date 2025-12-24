import pandas as pd
from typing import List, Dict

def recommend_daily_lineup(roster_stats: pd.DataFrame, opponent_stats: pd.DataFrame = None):
    """
    Simple recommender for daily lineup.
    For MVP, it sorts players by their average Z-score to maximize talent.
    If we had schedule data, we would prioritize players with games.
    
    roster_stats: DataFrame with 'player_id', 'full_name', 'z_total', 'next_game_date' (optional)
    """
    
    # Sort by Z-score
    if 'z_total' in roster_stats.columns:
        ranked = roster_stats.sort_values(by='z_total', ascending=False)
        return ranked
    
    return roster_stats
