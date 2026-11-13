"""Optional PostgreSQL adapter: owns SQLAlchemy pool and scoped sessions.

This is NOT a Supabase Auth client. No external connection is attempted at import.
"""
from collections.abc import Iterator
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

class Database:
    def __init__(self, url: str, *, pool_size: int = 2, max_overflow: int = 0,
                 pool_timeout: int = 10) -> None:
        if not url.startswith("postgresql+psycopg://") and not url.startswith("sqlite+pysqlite://"):
            raise ValueError("Unsupported database driver; use PostgreSQL/psycopg or local test SQLite")
        opts = {"pool_pre_ping": True}
        if url.startswith("postgresql+psycopg://"):
            opts.update(pool_size=pool_size, max_overflow=max_overflow, pool_timeout=pool_timeout,
                        connect_args={"connect_timeout": 5})
        self.engine: Engine = create_engine(url, **opts)
        self._session_factory = sessionmaker(self.engine, expire_on_commit=False)

    @contextmanager
    def session(self) -> Iterator[Session]:
        with self._session_factory() as session:
            try:
                yield session
                session.commit()
            except BaseException:
                session.rollback()
                raise

    def ping(self) -> bool:
        with self.engine.connect() as connection:
            return connection.execute(text("SELECT 1")).scalar_one() == 1

    def dispose(self) -> None:
        self.engine.dispose()
