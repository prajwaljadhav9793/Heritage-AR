from pathlib import Path

from app.database.db import get_connection


if __name__ == "__main__":
    database_path = Path(__file__).resolve().parents[2] / "database" / "heritagear.db"
    with get_connection(database_path) as connection:
        connection.execute("CREATE TABLE IF NOT EXISTS heritage_sites (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
        connection.commit()
