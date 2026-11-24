import os
import logging
from typing import List, Dict, Any, Optional
import asyncpg
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("mcp_db")


def get_db_dsn() -> str:
    """Resolve PostgreSQL DSN cleanly from environment."""
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        user = os.getenv("POSTGRES_USER", "postgres")
        pwd = os.getenv("POSTGRES_PASSWORD", "postgres")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "placement_db")
        dsn = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"
    elif dsn.startswith("postgresql+asyncpg://"):
        dsn = "postgresql://" + dsn[len("postgresql+asyncpg://"):]
    return dsn


async def query_db(sql: str, *args) -> Optional[List[Dict[str, Any]]]:
    """Execute parameterized read-only SQL query and return rows as dictionaries."""
    dsn = get_db_dsn()
    conn = None
    try:
        conn = await asyncpg.connect(dsn, timeout=5.0)
        rows = await conn.fetch(sql, *args)
        return [dict(r) for r in rows]
    except Exception as e:
        logger.warning(f"Database query failed ({sql[:60]}...): {e}")
        # Try fallback to port 5433 if running on host where port 5432 failed
        if ":5432/" in dsn:
            try:
                fallback_dsn = dsn.replace(":5432/", ":5433/")
                conn = await asyncpg.connect(fallback_dsn, timeout=3.0)
                rows = await conn.fetch(sql, *args)
                return [dict(r) for r in rows]
            except Exception:
                pass
        return None
    finally:
        if conn and not conn.is_closed():
            await conn.close()


async def query_one(sql: str, *args) -> Optional[Dict[str, Any]]:
    """Execute parameterized query and return single row as dict."""
    rows = await query_db(sql, *args)
    if rows:
        return rows[0]
    return None
