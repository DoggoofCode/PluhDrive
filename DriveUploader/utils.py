import sqlite3
from rich import print

class SQLite_Utils:
    @staticmethod
    def check_table_integrity(cursor):
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS Users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR NOT NULL,
                    password VARCHAR NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    time_deleted TIMESTAMP DEFAULT NULL
                )
            """)

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS FileSystems (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    parent_folder INTEGER,
                    name VARCHAR(50),
                    time_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    time_deleted TIMESTAMP DEFAULT NULL,
                    FOREIGN KEY (user_id) REFERENCES Users(id),
                    FOREIGN KEY (parent_folder) REFERENCES FileSystems(id)
                );
                """)

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS Manifests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name VARCHAR(50),
                    time_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    time_deleted TIMESTAMP DEFAULT NULL,
                    location INTEGER NOT NULL,
                    hash VARCHAR(64),
                    FOREIGN KEY (user_id) REFERENCES Users(id),
                    FOREIGN KEY (location) REFERENCES FileSystems(id)
                );
                """)

        cursor.connection.commit()

    @staticmethod
    def execute_query(cursor: sqlite3.Cursor, query: str):
        try:
            command_output = cursor.execute(query)
            print(f"Command Output: {command_output.fetchall()}")
        except sqlite3.Error as e:
            print(f"[red][bold]Error executing query: {e}[/red][/bold]")
        finally:
            cursor.connection.commit()
