from database import engine
from sqlalchemy import text


def _column_exists(conn, table_name, column_name):
    rows = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
    return any(row[1] == column_name for row in rows)


def _table_exists(conn, table_name):
    row = conn.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
        {"name": table_name},
    ).fetchone()
    return row is not None


with engine.connect() as conn:
    try:
        if _table_exists(conn, "users") and not _column_exists(conn, "users", "seller_status"):
            conn.execute(text("ALTER TABLE users ADD COLUMN seller_status VARCHAR(20) NOT NULL DEFAULT 'none'"))
            conn.commit()
            print("seller_status column added.")
        else:
            print("seller_status column already exists.")
    except Exception as e:
        print("Skipped seller_status migration:", e)

    try:
        if not _table_exists(conn, "seller_profiles"):
            conn.execute(text("""
                CREATE TABLE seller_profiles (
                    seller_profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    approved_at DATETIME NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
            """))
            conn.commit()
            print("seller_profiles table created.")
        else:
            print("seller_profiles table already exists.")
    except Exception as e:
        print("Skipped seller_profiles migration:", e)

    try:
        if not _table_exists(conn, "admin_profiles"):
            conn.execute(text("""
                CREATE TABLE admin_profiles (
                    admin_profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
            """))
            conn.commit()
            print("admin_profiles table created.")
        else:
            print("admin_profiles table already exists.")
    except Exception as e:
        print("Skipped admin_profiles migration:", e)
