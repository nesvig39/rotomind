"""
Configuration management for Fantasy NBA Assistant.

Handles environment variables and application settings.
"""

import os
from typing import Optional
from dataclasses import dataclass
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


@dataclass
class ESPNConfig:
    """ESPN Fantasy Basketball configuration."""
    league_id: Optional[int] = None
    espn_s2: Optional[str] = None
    swid: Optional[str] = None
    season: int = 2025
    
    @property
    def is_configured(self) -> bool:
        """Check if ESPN credentials are fully configured."""
        return all([self.league_id, self.espn_s2, self.swid])
    
    @classmethod
    def from_env(cls) -> "ESPNConfig":
        """Load ESPN configuration from environment variables."""
        league_id = os.getenv("ESPN_LEAGUE_ID")
        return cls(
            league_id=int(league_id) if league_id else None,
            espn_s2=os.getenv("ESPN_S2"),
            swid=os.getenv("ESPN_SWID"),
            season=int(os.getenv("ESPN_SEASON", "2025")),
        )


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 1800
    echo: bool = False
    
    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Load database configuration from environment variables."""
        url = os.getenv("DATABASE_URL")
        if not url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        # Handle Heroku-style postgres:// URLs
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        
        return cls(
            url=url,
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "1800")),
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
        )


@dataclass
class NBAApiConfig:
    """NBA API configuration."""
    min_request_interval: float = 0.6
    max_retries: int = 3
    timeout: int = 30
    use_mock: bool = False
    
    @classmethod
    def from_env(cls) -> "NBAApiConfig":
        """Load NBA API configuration from environment variables."""
        return cls(
            min_request_interval=float(os.getenv("NBA_API_INTERVAL", "0.6")),
            max_retries=int(os.getenv("NBA_API_RETRIES", "3")),
            timeout=int(os.getenv("NBA_API_TIMEOUT", "30")),
            use_mock=os.getenv("NBA_API_MOCK", "false").lower() == "true",
        )


@dataclass
class AppConfig:
    """Main application configuration."""
    database: DatabaseConfig
    espn: ESPNConfig
    nba_api: NBAApiConfig
    debug: bool = False
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load full application configuration from environment."""
        try:
            database = DatabaseConfig.from_env()
        except ValueError:
            # Allow app to load without database for testing
            database = None
            logger.warning("Database not configured")
        
        return cls(
            database=database,
            espn=ESPNConfig.from_env(),
            nba_api=NBAApiConfig.from_env(),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )


@lru_cache()
def get_config() -> AppConfig:
    """Get cached application configuration."""
    return AppConfig.from_env()


def configure_logging(config: Optional[AppConfig] = None):
    """Configure application logging."""
    if config is None:
        config = get_config()
    
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


# Environment variable documentation
ENV_VARS = """
# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/fantasy_nba
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800
DB_ECHO=false

# ESPN Fantasy Configuration
ESPN_LEAGUE_ID=12345678
ESPN_S2=your_espn_s2_cookie_value
ESPN_SWID=your_swid_cookie_value
ESPN_SEASON=2025

# NBA API Configuration
NBA_API_INTERVAL=0.6
NBA_API_RETRIES=3
NBA_API_TIMEOUT=30
NBA_API_MOCK=false

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
"""
