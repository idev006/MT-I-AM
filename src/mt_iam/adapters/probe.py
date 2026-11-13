"""One-shot DB-only connectivity check. No credentials printed; no schema mutations."""
from mt_iam.core.config import get_settings
from mt_iam.adapters.database import Database

def main() -> int:
    cfg = get_settings()
    if not cfg.database_url:
        print("BLOCKED: set MT_IAM_DATABASE_URL from approved secret source")
        return 2
    if not cfg.database_url.startswith("postgresql+psycopg://"):
        print("BLOCKED: probe requires PostgreSQL via psycopg")
        return 2
    database = Database(cfg.database_url, pool_size=cfg.db_pool_size,
                        max_overflow=cfg.db_max_overflow,
                        pool_timeout=cfg.db_pool_timeout)
    try:
        ok = database.ping()
        print("PASS: PostgreSQL SELECT 1" if ok else "FAIL: unexpected result")
        return 0 if ok else 1
    except Exception as error:
        print(f"FAIL: DB operation failed ({type(error).__name__}); secrets suppressed")
        return 1
    finally:
        database.dispose()

if __name__ == "__main__":
    raise SystemExit(main())
