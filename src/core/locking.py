from sqlmodel import Session, text
from contextlib import contextmanager
import hashlib
import os

class PostgresLock:
    def __init__(self, session: Session, key: str):
        self.session = session
        self.key_int = int(hashlib.sha256(key.encode('utf-8')).hexdigest(), 16) % (2**63 - 1)

    def acquire(self) -> bool:
        """Acquires a transaction-level advisory lock."""
        # Check dialect
        dialect = self.session.bind.dialect.name
        if dialect != 'postgresql':
            # For SQLite (tests), just return True or implement a dummy lock
            return True
            
        result = self.session.exec(text(f"SELECT pg_try_advisory_xact_lock({self.key_int})")).one()
        return result[0]

@contextmanager
def acquire_lock(session: Session, key: str):
    """
    Context manager for acquiring a lock.
    """
    lock = PostgresLock(session, key)
    if not lock.acquire():
        raise BlockingIOError(f"Could not acquire lock for resource: {key}")
    yield
