import sqlite3
from rich import print

class SQLite_Utils:
    @staticmethod
    def check_table_integrity(cursor):
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS Users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR NOT NULL UNIQUE,
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
        command_output = []
        try:
            command_output = cursor.execute(query)
            print(f"Command Output: {command_output.fetchall()}")
        except sqlite3.Error as e:
            print(f"[red][bold]Error executing query: {e}[/red][/bold]")
        finally:
            cursor.connection.commit()
        return command_output


    @staticmethod
    def safe_execute(cursor: sqlite3.Cursor, query: str, values: list | tuple):
        command_output = []
        try:
            command_output = cursor.execute(query, values)
        except sqlite3.Error as e:
            print(f"[red][bold]Error executing query: {e}[/red][/bold]")
        finally:
            cursor.connection.commit()
        return command_output


    @staticmethod
    def safe_insert(cursor: sqlite3.Cursor, table_name: str, item_names: list | tuple, values: list | tuple):
        try:
            cursor.execute(f"INSERT INTO {table_name} ({', '.join(item_names)}) VALUES ({', '.join(['?'] * len(values))})", values)
        except sqlite3.Error as e:
            print(f"[red][bold]Error inserting data: {e}[/red][/bold]")
        finally:
            cursor.connection.commit()


    @staticmethod
    def login(cursor: sqlite3.Cursor, login_args: list):
        try:
            password_phrase = " AND password = ?"
            cursor.execute(f"SELECT id FROM Users WHERE username = ?{password_phrase if len(login_args)>1 else ''}", (login_args))
            user_id = cursor.fetchone()[0]
            return user_id
        except sqlite3.Error as e:
            print(f"[red][bold]Error logging in: {e}[/red][/bold]")
            return None

    @staticmethod
    def make_folder(cursor: sqlite3.Cursor, folder_name: str, user_id: int, parent_id: int = 0):
        try:
            cursor.execute("INSERT INTO FileSystems (parent_folder, name, user_id) VALUES (?, ?, ?)", (parent_id, folder_name, user_id))
        except sqlite3.Error as e:
            print(f"[red][bold]Error creating folder: {e}[/red][/bold]")
        finally:
            cursor.connection.commit()

    @staticmethod
    def find_username_from_id(cursor: sqlite3.Cursor, user_id: int) -> str:
        try:
            cursor.execute("SELECT username FROM Users WHERE id = ?", (user_id,))
            username = cursor.fetchone()[0]
            return username
        except sqlite3.Error as e:
            print(f"[red][bold]Error finding username: {e}[/red][/bold]")
            return ""

    @staticmethod
    def find_id_from_username(cursor: sqlite3.Cursor, username: str) -> int:
        try:
            cursor.execute("SELECT id FROM Users WHERE username = ?", (username,))
            user_id = cursor.fetchone()[0]
            return user_id
        except sqlite3.Error as e:
            print(f"[red][bold]Error finding user ID: {e}[/red][/bold]")
            return 0
