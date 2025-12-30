from typing import List, Dict
import pandas as pd
from datetime import date
from sqlmodel import Session, select
from src.core.models import League, FantasyTeam, PlayerStats, DailyStandings

def calculate_roto_standings(session: Session, league_id: int, calculation_date: date = None):
    """
    Calculates Roto standings for a league.
    1. Aggregates stats for all players in each team up to calculation_date.
    2. Ranks teams in each category.
    3. Assigns points (1 to N).
    4. Saves/Returns DailyStandings.
    """
    if calculation_date is None:
        calculation_date = date.today()
        
    league = session.get(League, league_id)
    if not league or not league.teams:
        return []
        
    # 1. Aggregate Stats per Team
    team_stats = []
    
    for team in league.teams:
        # Get all player IDs in roster
        # In a real app with historical rosters, we'd check who was on the team on each date.
        # MVP: Assuming current roster applies to all history (Simplification)
        player_ids = [p.id for p in team.players]
        if not player_ids:
            # Empty team
            team_stats.append({
                'team_id': team.id, 'pts': 0, 'reb': 0, 'ast': 0, 'stl': 0, 'blk': 0, 
                'fgm': 0, 'fga': 0, 'ftm': 0, 'fta': 0, 'tpm': 0
            })
            continue
            
        # Sum stats for these players up to date
        stmt = select(PlayerStats).where(
            PlayerStats.player_id.in_(player_ids),
            PlayerStats.game_date <= calculation_date
        )
        stats = session.exec(stmt).all()
        
        # Aggregate
        t_data = {
            'team_id': team.id,
            'pts': sum(s.pts for s in stats),
            'reb': sum(s.reb for s in stats),
            'ast': sum(s.ast for s in stats),
            'stl': sum(s.stl for s in stats),
            'blk': sum(s.blk for s in stats),
            'fgm': sum(s.fgm for s in stats),
            'fga': sum(s.fga for s in stats),
            'ftm': sum(s.ftm for s in stats),
            'fta': sum(s.fta for s in stats),
            'tpm': sum(s.tpm for s in stats),
        }
        team_stats.append(t_data)
        
    df = pd.DataFrame(team_stats)
    if df.empty:
        return []
        
    # Calculate Percentages
    # Avoid div/0
    df['fg_pct'] = df.apply(lambda x: x['fgm'] / x['fga'] if x['fga'] > 0 else 0, axis=1)
    df['ft_pct'] = df.apply(lambda x: x['ftm'] / x['fta'] if x['fta'] > 0 else 0, axis=1)
    
    # 2. Rank and Assign Points
    # 8 Categories: PTS, REB, AST, STL, BLK, 3PM, FG%, FT%
    cats = {
        'pts': 'points_pts',
        'reb': 'points_reb',
        'ast': 'points_ast',
        'stl': 'points_stl',
        'blk': 'points_blk',
        'tpm': 'points_tpm',
        'fg_pct': 'points_fg_pct',
        'ft_pct': 'points_ft_pct'
    }
    
    # Initialize Roto Points columns
    for col in cats.values():
        df[col] = 0.0
        
    # Rank (method='min' means ties get same rank, but standard roto often splits points. 
    # MVP: Simple rank 1..N. Using 'average' for ties is standard roto)
    for stat_col, point_col in cats.items():
        # ascending=True for turnovers if 9-cat. For 8-cat all are ascending.
        df[point_col] = df[stat_col].rank(ascending=True, method='average')
        
    # Total Roto Points
    df['total_roto_points'] = df[[c for c in cats.values()]].sum(axis=1)
    df['rank'] = df['total_roto_points'].rank(ascending=False, method='min')
    
    # 3. Save to DB
    results = []
    for _, row in df.iterrows():
        # Check if exists
        stmt = select(DailyStandings).where(
            DailyStandings.league_id == league_id,
            DailyStandings.team_id == int(row['team_id']),
            DailyStandings.date == calculation_date
        )
        existing = session.exec(stmt).first()
        
        if existing:
            ds = existing
        else:
            ds = DailyStandings(
                league_id=league_id,
                team_id=int(row['team_id']),
                date=calculation_date
            )
            
        # Update fields
        ds.total_pts = int(row['pts'])
        ds.total_reb = int(row['reb'])
        ds.total_ast = int(row['ast'])
        ds.total_stl = int(row['stl'])
        ds.total_blk = int(row['blk'])
        ds.total_fgm = int(row['fgm'])
        ds.total_fga = int(row['fga'])
        ds.total_ftm = int(row['ftm'])
        ds.total_fta = int(row['fta'])
        ds.total_tpm = int(row['tpm'])
        
        ds.points_pts = float(row['points_pts'])
        ds.points_reb = float(row['points_reb'])
        ds.points_ast = float(row['points_ast'])
        ds.points_stl = float(row['points_stl'])
        ds.points_blk = float(row['points_blk'])
        ds.points_tpm = float(row['points_tpm'])
        ds.points_fg_pct = float(row['points_fg_pct'])
        ds.points_ft_pct = float(row['points_ft_pct'])
        
        ds.total_roto_points = float(row['total_roto_points'])
        ds.rank = int(row['rank'])
        
        session.add(ds)
        results.append(ds)
        
    session.commit()
    return results
