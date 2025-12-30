from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from sqlmodel import Session, select
from src.core.models import Player, PlayerStats
from src.core.db import engine
from datetime import datetime, timedelta
import time
import pandas as pd
import random
from requests.exceptions import ReadTimeout, ConnectionError

class NBAClient:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.nba.com/',
            'Origin': 'https://www.nba.com/'
        }

    def fetch_active_players(self, mock=False):
        """Fetches all active players and returns them as a list of dicts."""
        if mock:
            return self._generate_mock_players()
            
        # Check if we can reach the API, otherwise mock
        try:
            nba_players = players.get_active_players()
            if not nba_players:
                raise Exception("Empty list")
            return nba_players
        except Exception as e:
            print(f"Error fetching players, using mock data: {e}")
            return self._generate_mock_players()

    def fetch_player_stats(self, player_id: int, season='2024-25', retries=3, mock=False):
        """Fetches game log for a specific player with retries. Fallback to mock on failure."""
        if mock:
             return self._generate_mock_stats(player_id)
             
        for attempt in range(retries):
            time.sleep(1.0 * (attempt + 1)) 
            try:
                gamelog = playergamelog.PlayerGameLog(
                    player_id=player_id, 
                    season=season, 
                    headers=self.headers,
                    timeout=5 
                )
                df = gamelog.get_data_frames()[0]
                if not df.empty:
                    return df
            except Exception as e:
                print(f"Attempt {attempt+1}/{retries} failed for {player_id}: {e}")
        
        print(f"Returning mock stats for {player_id} due to API failure.")
        return self._generate_mock_stats(player_id)

    def _generate_mock_players(self):
        """Generates a list of dummy players for MVP testing."""
        return [
            {'id': 201939, 'full_name': 'Stephen Curry', 'is_active': True},
            {'id': 2544, 'full_name': 'LeBron James', 'is_active': True},
            {'id': 203999, 'full_name': 'Nikola Jokic', 'is_active': True},
            {'id': 1629029, 'full_name': 'Luka Doncic', 'is_active': True},
            {'id': 203507, 'full_name': 'Giannis Antetokounmpo', 'is_active': True},
        ]

    def _generate_mock_stats(self, player_id: int):
        """Generates random stats for a player."""
        dates = [datetime.now() - timedelta(days=x) for x in range(10)]
        data = []
        for d in dates:
            data.append({
                'Game_ID': f"0022400{random.randint(100,999)}",
                'GAME_DATE': d.strftime("%b %d, %Y"),
                'MATCHUP': 'GSW vs LAL',
                'PTS': random.randint(15, 35),
                'REB': random.randint(2, 12),
                'AST': random.randint(2, 12),
                'STL': random.randint(0, 3),
                'BLK': random.randint(0, 2),
                'FGM': random.randint(5, 12),
                'FGA': random.randint(10, 25),
                'FTM': random.randint(2, 8),
                'FTA': random.randint(2, 10),
                'FG3M': random.randint(0, 6),
                'TOV': random.randint(1, 5)
            })
        return pd.DataFrame(data)

    def sync_players(self, db_engine, mock=False):
        """Syncs active players to the database. Creates its own session."""
        with Session(db_engine) as session:
            active_players = self.fetch_active_players(mock=mock)
            count = 0
            for p in active_players:
                # Check if exists
                statement = select(Player).where(Player.nba_id == p['id'])
                results = session.exec(statement)
                existing_player = results.first()
                
                if not existing_player:
                    new_player = Player(
                        nba_id=p['id'],
                        full_name=p['full_name'],
                        is_active=p['is_active']
                    )
                    session.add(new_player)
                    count += 1
            
            session.commit()
            print(f"Synced {count} new players.")

    def sync_recent_stats(self, db_engine, days=15, limit_players=None, mock=False):
        """
        Syncs stats for players. Creates its own session.
        limit_players: Integer to limit how many players to sync (for testing/MVP speed).
        """
        with Session(db_engine) as session:
            statement = select(Player).where(Player.is_active == True)
            players_db = session.exec(statement).all()
            
            if limit_players:
                players_db = players_db[:limit_players]

            print(f"Syncing stats for {len(players_db)} players...")
            
            for p in players_db:
                df = self.fetch_player_stats(p.nba_id, mock=mock)
                if df.empty:
                    continue
                
                for _, row in df.iterrows():
                    game_date_str = row['GAME_DATE']
                    try:
                        game_date = datetime.strptime(game_date_str, "%b %d, %Y").date()
                    except ValueError:
                        continue
                    
                    # Check duplication
                    stmt = select(PlayerStats).where(
                        PlayerStats.player_id == p.id,
                        PlayerStats.game_id == row['Game_ID']
                    )
                    if session.exec(stmt).first():
                        continue

                    stats = PlayerStats(
                        player_id=p.id,
                        game_date=game_date,
                        game_id=row['Game_ID'],
                        matchup=row['MATCHUP'],
                        pts=row['PTS'],
                        reb=row['REB'],
                        ast=row['AST'],
                        stl=row['STL'],
                        blk=row['BLK'],
                        fgm=row['FGM'],
                        fga=row['FGA'],
                        ftm=row['FTM'],
                        fta=row['FTA'],
                        tpm=row['FG3M'],
                        tov=row['TOV']
                    )
                    session.add(stats)
                
                session.commit()
