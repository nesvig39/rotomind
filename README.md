# 🏀 Fantasy NBA Assistant (Rotomind)

An AI-powered assistant for Fantasy NBA 8-Cat Rotisserie leagues. This application helps you manage your team, analyze trades, optimize daily lineups, and track real-time roto standings.

## 🚀 Features

*   **Roto Standings Engine**: Automatically calculates 8-category rotisserie standings (ranking teams 1-N per category) based on aggregated player stats.
*   **League Setup Wizard**: Bulk import teams and rosters using a simple JSON map (with fuzzy matching for player names).
*   **Trade Analyzer**: Simulate trades between teams and visualize the impact on Z-scores and projected standings.
*   **Daily Lineup Recommendations**: Get recommendations on who to start based on player performance (Z-scores).
*   **Player Explorer**: View and sort players by their season-long Z-scores across all 8 categories.
*   **Data Ingestion**: Fetches live data from the NBA API (with a mock mode for offline development).

## 🛠️ Tech Stack

*   **Backend**: Python, FastAPI
*   **Frontend**: Streamlit
*   **Database**: PostgreSQL
*   **ORM**: SQLModel (SQLAlchemy + Pydantic)
*   **Data Source**: `nba_api`

## 📦 Installation & Setup

### Prerequisites

*   Python 3.9+
*   PostgreSQL installed and running
*   Git

### 1. Clone the Repository

```bash
git clone https://github.com/nesvig39/rotomind.git
cd rotomind
```

### 2. Set Up Environment

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Database

Ensure PostgreSQL is running. Set the `DATABASE_URL` environment variable.

On Linux/Mac:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/fantasy_nba"
```

On Windows (PowerShell):
```powershell
$env:DATABASE_URL = "postgresql://user:password@localhost:5432/fantasy_nba"
```

*Note: The application will log a warning but won't crash if the database is unreachable on startup, but functionality will be limited.*

### 4. Run the Application

You need to run both the Backend API and the Frontend Dashboard.

**Terminal 1: Backend API**
```bash
uvicorn app:app --reload
```
*API docs available at: http://localhost:8000/docs*

**Terminal 2: Frontend Dashboard**
```bash
streamlit run dashboard.py
```
*Dashboard available at: http://localhost:8501*

## 🧪 Running Tests

Integration tests use a temporary SQLite database to ensure isolation.

```bash
python -m pytest test_integration.py -v
```

## 📂 Project Structure

```
rotomind/
├── app.py              # FastAPI application endpoints
├── models.py           # SQLModel database models
├── db.py               # Database connection and session management
├── stats.py            # Z-score calculation engine
├── roto.py             # Roto standings calculator
├── analyzer.py         # Trade analysis logic
├── recommender.py      # Lineup recommendation engine
├── supervisor.py       # Background task supervisor/agent system
├── importer.py         # Roster import with fuzzy matching
├── locking.py          # Database advisory locks
├── nba_client.py       # NBA API client for data ingestion
├── dashboard.py        # Streamlit frontend UI
├── test_integration.py # Integration tests
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
├── .gitignore          # Git ignore patterns
├── ARCHITECTURE.md     # System architecture documentation
├── DEPLOYMENT.md       # Deployment instructions
└── README.md           # This file
```

## 📖 Usage Guide

1.  **Ingest Data**: Go to the sidebar in the Dashboard and click "Run Data Ingestion" to fetch the latest players and stats.
2.  **Create League**: Navigate to the "Leagues" tab. Create a new league or use the "League Setup Wizard" to bulk import teams.
3.  **Manage Teams**: Use the "My Teams" tab to view rosters or add individual players.
4.  **Analyze**: Use the "Trade Analyzer" tab to compare potential trades or "Dashboard" for daily start/sit advice.
