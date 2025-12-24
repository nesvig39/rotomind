# Fantasy NBA Roto Assistant - MVP Architecture

## Overview

This system is designed as a local MVP to assist Fantasy NBA owners in 8-cat Rotisserie leagues. It provides recommendations for daily lineups, analyzes trades, and suggests free agent pickups.

## Tech Stack

- **Language**: Python 3.9+
- **Database**: PostgreSQL
- **API Framework**: FastAPI
- **Frontend**: Streamlit (Data-centric UI)
- **Data Manipulation**: Pandas, NumPy
- **Data Source**: `nba_api` (Python wrapper for NBA.com API)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)

## System Components

### 1. Data Ingestion Layer (`/ingestion`)
Responsible for fetching raw data from external sources.
- **Players**: Active roster lists.
- **Stats**: Daily box scores, season averages.
- **Schedule**: NBA schedule for games played maximization.

### 2. Core Logic / Domain Layer (`/core`)
Contains the business logic and mathematical models.
- **Stats Engine**: Calculates Z-scores for 8 categories (PTS, REB, AST, STL, BLK, 3PM, FG%, FT%).
- **Roto Calculator**: Determines standings based on category totals/averages.
- **Recommendation Engine**:
    - *Lineup*: Who to start based on opponent and recent performance.
    - *Trade*: Impact analysis on team Z-scores and projected standings.
    - *Waiver Wire*: Identifies free agents with positive impact relative to worst rostered players.

### 3. API Layer (`/api`)
Exposes the core logic via REST endpoints for the frontend or other consumers.
- `/players`: List players and stats.
- `/teams`: Team rosters and current standings.
- `/analyze/trade`: Endpoint to simulate trades.
- `/analyze/lineup`: Endpoint for daily suggestions.

### 4. Frontend Layer (`/ui`)
A Streamlit dashboard for the user.
- **Dashboard**: High-level view of current standings and today's optimal lineup.
- **Trade Analyzer**: Interactive tool to select players and see results.
- **Player Explorer**: Searchable table of players with calculated values.

## Data Model (Simplified)

- **Player**: ID, Name, Team, Position.
- **PlayerStats**: PlayerID, GameDate, PTS, REB, etc.
- **FantasyTeam**: ID, Name, List of PlayerIDs.
- **LeagueSettings**: 8-cat definition, Roster spots.

## Directory Structure

```
fantasy_nba/
├── data/               # SQLite db and raw files
├── src/
│   ├── api/            # FastAPI app
│   ├── core/           # Logic and Models
│   ├── ingestion/      # Data fetching scripts
│   ├── ui/             # Streamlit app
│   └── main.py         # Entry point
├── requirements.txt
├── ARCHITECTURE.md
└── README.md
```
