"""Database session management."""
from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import get_settings

Base = declarative_base()


class Database:
    """Encapsulate SQLAlchemy engine and session handling."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._engine = create_engine(self._settings.postgres_url, future=True, pool_pre_ping=True)
        self._session_factory = sessionmaker(bind=self._engine, class_=Session, expire_on_commit=False)

    @contextmanager
    def session(self) -> Session:
        session: Session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


db = Database()
