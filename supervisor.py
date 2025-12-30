from typing import Dict, Any, Type
from sqlmodel import Session, select
from datetime import datetime, timezone
import traceback
import logging

from models import AgentTask, AuditLog, utc_now
import db as db_module  # Import module for late binding of engine
from locking import acquire_lock
from roto import calculate_roto_standings
from importer import RosterImporter
from nba_client import NBAClient

# Logger
logger = logging.getLogger(__name__)

class BaseAgent:
    """Abstract base class for all agents."""
    def run(self, session: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

class RotoAgent(BaseAgent):
    def run(self, session: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
        league_id = payload.get("league_id")
        if not league_id:
            raise ValueError("league_id required")
            
        with acquire_lock(session, f"league_{league_id}"):
            results = calculate_roto_standings(session, league_id)
            
            # Log Audit
            audit = AuditLog(
                entity_type="League",
                entity_id=league_id,
                action="calculate_standings",
                details={"teams_processed": len(results)}
            )
            session.add(audit)
            
            return {"status": "success", "count": len(results)}

class ImportAgent(BaseAgent):
    def run(self, session: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
        league_id = payload.get("league_id")
        roster_map = payload.get("roster_map")
        
        if not league_id or not roster_map:
            raise ValueError("league_id and roster_map required")
            
        with acquire_lock(session, f"league_{league_id}"):
            importer = RosterImporter(session)
            report = importer.process_import(league_id, roster_map)
            
            audit = AuditLog(
                entity_type="League",
                entity_id=league_id,
                action="import_rosters",
                details=report
            )
            session.add(audit)
            return report

class IngestionAgent(BaseAgent):
    def run(self, session: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
        days = payload.get("days", 15)
        mock = payload.get("mock", False)
        
        with acquire_lock(session, "global_ingest"):
            client = NBAClient()
            # Pass the global engine (late bound)
            client.sync_players(db_module.engine, mock=mock) 
            client.sync_recent_stats(db_module.engine, days=days, mock=mock)
            return {"status": "ingestion_complete"}

class Supervisor:
    """
    Manages task execution and agent delegation.
    """
    _agents: Dict[str, Type[BaseAgent]] = {
        "calculate_roto": RotoAgent,
        "import_roster": ImportAgent,
        "ingest_data": IngestionAgent
    }

    @classmethod
    def submit_task(cls, task_type: str, payload: Dict[str, Any]) -> AgentTask:
        """
        Creates a task record. 
        """
        # Use db_module.engine to ensure we get the patched engine during tests
        with Session(db_module.engine) as session:
            task = AgentTask(task_type=task_type, payload=payload, status="pending")
            session.add(task)
            session.commit()
            session.refresh(task)
            return task

    @classmethod
    def run_task(cls, task_id: str):
        """
        Executes a task. Should be called by a worker or BackgroundTask.
        """
        with Session(db_module.engine) as session:
            task = session.get(AgentTask, task_id)
            if not task:
                logger.error(f"Task {task_id} not found")
                return

            if task_type := cls._agents.get(task.task_type):
                agent = task_type()
                
                try:
                    task.status = "running"
                    session.add(task)
                    session.commit()
                    
                    # Execute Agent Logic
                    result = agent.run(session, task.payload)
                    
                    task.result = result
                    task.status = "completed"
                except BlockingIOError:
                    task.status = "failed"
                    task.error = "Resource locked. Try again later."
                except Exception as e:
                    logger.error(f"Task failed: {e}")
                    task.status = "failed"
                    task.error = str(e)
                    task.result = {"traceback": traceback.format_exc()}
                finally:
                    task.updated_at = utc_now()
                    session.add(task)
                    session.commit()
            else:
                task.status = "failed"
                task.error = f"Unknown task type: {task.task_type}"
                session.add(task)
                session.commit()
