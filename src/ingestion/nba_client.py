from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from sqlmodel import Session, select
from src.core.models import Player, PlayerStats
from src.core.db import engine
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass
import time
import pandas as pd
import random
import logging
from requests.exceptions import ReadTimeout, ConnectionError

logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Result of a sync operation."""
    success: bool
    records_created: int = 0
    records_updated: int = 0
    records_skipped: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "records_created": self.records_created,
            "records_updated": self.records_updated,
            "records_skipped": self.records_skipped,
            "errors": self.errors,
        }


class NBAClient:
    """Client for fetching NBA data and syncing to database."""
    
    # Rate limiting configuration
    MIN_REQUEST_INTERVAL = 0.6  # Minimum seconds between API requests
    MAX_RETRIES = 3
    BATCH_SIZE = 100  # Number of records to batch before committing
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.nba.com/',
            'Origin': 'https://www.nba.com/'
        }
        self._last_request_time = 0

    def _rate_limit(self):
        """Enforce rate limiting between API requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.MIN_REQUEST_INTERVAL:
            time.sleep(self.MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.time()

    def fetch_active_players(self, mock: bool = False) -> List[Dict[str, Any]]:
        """Fetches all active players and returns them as a list of dicts."""
        if mock:
            logger.info("Using mock player data")
            return self._generate_mock_players()
        
        self._rate_limit()
        try:
            nba_players = players.get_active_players()
            if not nba_players:
                raise ValueError("NBA API returned empty player list")
            logger.info(f"Fetched {len(nba_players)} active players from NBA API")
            return nba_players
        except Exception as e:
            logger.warning(f"Error fetching players from NBA API: {e}. Using mock data.")
            return self._generate_mock_players()

    def fetch_player_stats(
        self, 
        player_id: int, 
        season: str = '2024-25', 
        mock: bool = False
    ) -> pd.DataFrame:
        """
        Fetches game log for a specific player with retries.
        
        Args:
            player_id: NBA player ID
            season: Season string (e.g., '2024-25')
            mock: If True, return mock data
            
        Returns:
            DataFrame with player game stats
        """
        if mock:
            return self._generate_mock_stats(player_id)
        
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            self._rate_limit()
            try:
                gamelog = playergamelog.PlayerGameLog(
                    player_id=player_id, 
                    season=season, 
                    headers=self.headers,
                    timeout=10  # Increased timeout
                )
                df = gamelog.get_data_frames()[0]
                if not df.empty:
                    logger.debug(f"Fetched {len(df)} games for player {player_id}")
                    return df
                return pd.DataFrame()  # Return empty DataFrame if no data
            except (ReadTimeout, ConnectionError) as e:
                last_error = e
                wait_time = (attempt + 1) * 2  # Exponential backoff
                logger.warning(
                    f"Attempt {attempt+1}/{self.MAX_RETRIES} failed for player {player_id}: {e}. "
                    f"Waiting {wait_time}s..."
                )
                time.sleep(wait_time)
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error fetching stats for player {player_id}: {e}")
                break
        
        logger.warning(f"All retries failed for player {player_id}. Last error: {last_error}")
        return pd.DataFrame()  # Return empty DataFrame instead of mock to avoid mixing real/fake data

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

    def sync_players(
        self, 
        db_engine, 
        mock: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> SyncResult:
        """
        Syncs active players to the database with batch processing.
        
        Args:
            db_engine: SQLAlchemy engine
            mock: If True, use mock data
            progress_callback: Optional callback(current, total) for progress updates
            
        Returns:
            SyncResult with operation details
        """
        result = SyncResult(success=False)
        
        with Session(db_engine) as session:
            try:
                active_players = self.fetch_active_players(mock=mock)
                total = len(active_players)
                
                if not active_players:
                    logger.warning("No players fetched from source")
                    result.success = True
                    return result
                
                # Pre-fetch existing NBA IDs for efficient lookup (avoid N+1)
                existing_ids = set(
                    session.exec(select(Player.nba_id)).all()
                )
                logger.info(f"Found {len(existing_ids)} existing players in database")
                
                new_players = []
                for idx, p in enumerate(active_players):
                    # Validate required fields
                    if not p.get('id') or not p.get('full_name'):
                        result.errors.append(f"Invalid player data: {p}")
                        result.records_skipped += 1
                        continue
                    
                    if p['id'] in existing_ids:
                        result.records_skipped += 1
                        continue
                    
                    new_player = Player(
                        nba_id=p['id'],
                        full_name=p['full_name'],
                        is_active=p.get('is_active', True)
                    )
                    new_players.append(new_player)
                    result.records_created += 1
                    
                    # Batch commit for performance
                    if len(new_players) >= self.BATCH_SIZE:
                        session.add_all(new_players)
                        session.commit()
                        logger.debug(f"Committed batch of {len(new_players)} players")
                        new_players = []
                    
                    if progress_callback:
                        progress_callback(idx + 1, total)
                
                # Commit remaining players
                if new_players:
                    session.add_all(new_players)
                    session.commit()
                
                result.success = True
                logger.info(
                    f"Player sync complete: {result.records_created} created, "
                    f"{result.records_skipped} skipped"
                )
                
            except Exception as e:
                session.rollback()
                result.errors.append(str(e))
                logger.error(f"Player sync failed: {e}")
                
        return result

    def _parse_game_date(self, date_str: str) -> Optional[datetime]:
        """Parse game date from various formats."""
        formats = ["%b %d, %Y", "%Y-%m-%d", "%m/%d/%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None

    def _validate_stat_row(self, row: pd.Series) -> List[str]:
        """Validate a stats row and return list of errors."""
        errors = []
        required_fields = ['Game_ID', 'GAME_DATE', 'MATCHUP']
        for field in required_fields:
            if field not in row or pd.isna(row[field]):
                errors.append(f"Missing required field: {field}")
        
        # Validate numeric fields are non-negative
        numeric_fields = ['PTS', 'REB', 'AST', 'STL', 'BLK', 'FGM', 'FGA', 'FTM', 'FTA', 'FG3M', 'TOV']
        for field in numeric_fields:
            if field in row and not pd.isna(row[field]):
                if row[field] < 0:
                    errors.append(f"Negative value for {field}: {row[field]}")
        
        return errors

    def sync_recent_stats(
        self, 
        db_engine, 
        days: int = 15, 
        limit_players: Optional[int] = None, 
        mock: bool = False,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> SyncResult:
        """
        Syncs stats for players with batch processing and validation.
        
        Args:
            db_engine: SQLAlchemy engine
            days: Number of days to sync (not currently filtered, fetches full season)
            limit_players: Maximum number of players to sync (for testing)
            mock: If True, use mock data
            progress_callback: Optional callback(current, total, player_name) for progress
            
        Returns:
            SyncResult with operation details
        """
        result = SyncResult(success=False)
        
        with Session(db_engine) as session:
            try:
                statement = select(Player).where(Player.is_active == True)
                players_db = session.exec(statement).all()
                
                if limit_players:
                    players_db = players_db[:limit_players]
                
                total_players = len(players_db)
                logger.info(f"Syncing stats for {total_players} players...")
                
                # Pre-fetch existing game IDs per player for efficient dedup
                existing_games_stmt = select(
                    PlayerStats.player_id, 
                    PlayerStats.game_id
                )
                existing_games = session.exec(existing_games_stmt).all()
                existing_game_set = set((pg.player_id, pg.game_id) for pg in existing_games)
                logger.info(f"Found {len(existing_game_set)} existing game records")
                
                stats_batch = []
                
                for idx, player in enumerate(players_db):
                    if progress_callback:
                        progress_callback(idx + 1, total_players, player.full_name)
                    
                    df = self.fetch_player_stats(player.nba_id, mock=mock)
                    
                    if df is None or df.empty:
                        logger.debug(f"No stats found for {player.full_name}")
                        continue
                    
                    for _, row in df.iterrows():
                        game_id = row.get('Game_ID')
                        
                        # Check for duplicate
                        if (player.id, game_id) in existing_game_set:
                            result.records_skipped += 1
                            continue
                        
                        # Validate row
                        validation_errors = self._validate_stat_row(row)
                        if validation_errors:
                            result.errors.append(
                                f"Player {player.id}, Game {game_id}: {validation_errors}"
                            )
                            result.records_skipped += 1
                            continue
                        
                        # Parse date
                        game_date = self._parse_game_date(row['GAME_DATE'])
                        if not game_date:
                            result.errors.append(
                                f"Invalid date format: {row['GAME_DATE']} for game {game_id}"
                            )
                            result.records_skipped += 1
                            continue
                        
                        # Create stats record with safe defaults for missing numeric fields
                        stats = PlayerStats(
                            player_id=player.id,
                            game_date=game_date,
                            game_id=game_id,
                            matchup=row['MATCHUP'],
                            pts=int(row.get('PTS', 0) or 0),
                            reb=int(row.get('REB', 0) or 0),
                            ast=int(row.get('AST', 0) or 0),
                            stl=int(row.get('STL', 0) or 0),
                            blk=int(row.get('BLK', 0) or 0),
                            fgm=int(row.get('FGM', 0) or 0),
                            fga=int(row.get('FGA', 0) or 0),
                            ftm=int(row.get('FTM', 0) or 0),
                            fta=int(row.get('FTA', 0) or 0),
                            tpm=int(row.get('FG3M', 0) or 0),
                            tov=int(row.get('TOV', 0) or 0)
                        )
                        stats_batch.append(stats)
                        existing_game_set.add((player.id, game_id))  # Prevent in-batch dupes
                        result.records_created += 1
                        
                        # Batch commit for performance
                        if len(stats_batch) >= self.BATCH_SIZE:
                            session.add_all(stats_batch)
                            session.commit()
                            logger.debug(f"Committed batch of {len(stats_batch)} stats records")
                            stats_batch = []
                
                # Commit remaining records
                if stats_batch:
                    session.add_all(stats_batch)
                    session.commit()
                    logger.debug(f"Committed final batch of {len(stats_batch)} stats records")
                
                result.success = True
                logger.info(
                    f"Stats sync complete: {result.records_created} created, "
                    f"{result.records_skipped} skipped, {len(result.errors)} errors"
                )
                
            except Exception as e:
                session.rollback()
                result.errors.append(str(e))
                logger.error(f"Stats sync failed: {e}", exc_info=True)
        
        return result
