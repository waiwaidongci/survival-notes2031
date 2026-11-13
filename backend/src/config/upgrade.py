"""Idempotent column upgrades so pre-roll studies stay readable after deploy."""
import logging
from sqlalchemy import text
from .database import engine
from ..constants.bootstrap import DEFAULT_SEED
def ensure_schema():
    statements=[("specimens","roll_no","ALTER TABLE specimens ADD COLUMN roll_no VARCHAR(40) NULL"),("survival_runs","seed",f"ALTER TABLE survival_runs ADD COLUMN seed INT NOT NULL DEFAULT {DEFAULT_SEED}")]
    try:
        with engine.connect() as conn:
            for table,column,ddl in statements:
                exists=conn.execute(text("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=:t AND COLUMN_NAME=:c"),{"t":table,"c":column}).scalar()
                if not exists:
                    try:conn.execute(text(ddl));conn.commit()
                    except Exception:logging.exception("schema upgrade failed: %s.%s",table,column)
    except Exception:logging.exception("schema upgrade check failed")
