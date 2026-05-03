from database import engine
from sqlalchemy import text


def _column_exists(conn, table_name, column_name):
    rows = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
    return any(row[1] == column_name for row in rows)


with engine.connect() as conn:
    try:
        if not _column_exists(conn, "users", "role"):
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'customer'"))
            conn.commit()
            print("role column added.")
        else:
            print("role column already exists.")
    except Exception as e:
        print("Skipped role migration:", e)

    try:
        if not _column_exists(conn, "users", "is_active"):
            conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1"))
            conn.commit()
            print("is_active column added.")
        else:
            print("is_active column already exists.")
    except Exception as e:
        print("Skipped is_active migration:", e)
