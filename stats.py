import pandas as pd
from typing import List, Dict

def calculate_z_scores(df: pd.DataFrame, categories: List[str] = None):
    """
    Calculates Z-scores for the given dataframe of player averages.
    df: DataFrame with player names and stats columns.
    categories: List of categories to calculate Z-scores for (default 8-cat).
    """
    if categories is None:
        categories = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'FG3M', 'FG_PCT', 'FT_PCT']
        
    stats_df = df.copy()
    
    # Calculate averages and std dev for the population
    means = stats_df[categories].mean()
    stds = stats_df[categories].std()
    
    z_score_cols = []
    for cat in categories:
        col_name = f"z_{cat}"
        z_score_cols.append(col_name)
        # Avoid division by zero
        if stds[cat] == 0:
            stats_df[col_name] = 0.0
        else:
            stats_df[col_name] = (stats_df[cat] - means[cat]) / stds[cat]
            
    # Calculate Total Z-score (average of z-scores)
    stats_df['z_total'] = stats_df[z_score_cols].mean(axis=1)
    
    return stats_df.sort_values(by='z_total', ascending=False)

def aggregate_player_stats(stats_data: List[Dict]):
    """
    Aggregates a list of stat dictionaries (from DB) into per-player averages.
    """
    if not stats_data:
        return pd.DataFrame()
        
    df = pd.DataFrame(stats_data)
    
    # Check if we have percent categories, if not calculate them from FGM/FGA etc
    if 'FG_PCT' not in df.columns:
        # Sum totals first
        sums = df.groupby('player_id').sum(numeric_only=True).reset_index()
        sums['FG_PCT'] = sums.apply(lambda x: x['fgm']/x['fga'] if x['fga'] > 0 else 0, axis=1)
        sums['FT_PCT'] = sums.apply(lambda x: x['ftm']/x['fta'] if x['fta'] > 0 else 0, axis=1)
        
        # Rename columns to match standard 8-cat headers expected
        sums = sums.rename(columns={
            'pts': 'PTS', 'reb': 'REB', 'ast': 'AST', 
            'stl': 'STL', 'blk': 'BLK', 'tpm': 'FG3M'
        })
        
        # Since we summed, we need averages for counting stats? 
        # Actually for Z-scores usually we use per-game averages.
        # So let's count games.
        counts = df.groupby('player_id').size().reset_index(name='games')
        sums = sums.merge(counts, on='player_id')
        
        for col in ['PTS', 'REB', 'AST', 'STL', 'BLK', 'FG3M']:
            sums[col] = sums[col] / sums['games']
            
        return sums
        
    return df
