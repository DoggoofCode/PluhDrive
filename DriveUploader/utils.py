import sqlite3
from DriveUploader.SQLCommands import SQL_Executor as sql
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
        command_output = sql.execute_query(cursor, query)
        print(f"Command Output: {command_output}")
        return command_output


    @staticmethod
    def safe_execute(cursor: sqlite3.Cursor, query: str, values: list[str]):
        command_output = []
        command_output = sql.execute_query(cursor, query, values)
        return command_output


    @staticmethod
    def safe_insert(cursor: sqlite3.Cursor, table_name: str, item_names: list | tuple, values: list | tuple):
        command = f"INSERT INTO {table_name} ({', '.join(item_names)}) VALUES ({', '.join(['?'] * len(values))})"
        sql.execute_query(cursor, command, values)

    @staticmethod
    def util_execute(cursor: sqlite3.Cursor, cmd:str) -> None:
        try:
            m = eval(cmd)
            print(m)
        except Exception as e:
            print(f"[red][bold]Error[/red][/bold]: {e}")

    @staticmethod
    def login(cursor: sqlite3.Cursor, login_args: list) -> int | None:
        # password_phrase = " AND password = ?"
        # command = f"SELECT id FROM Users WHERE username = ?{password_phrase if len(login_args)>1 else ''}"
        # sql.execute_query(cursor, command, login_args)
        outpt = sql.execute_select(cursor, "Users", "username", login_args)
        if outpt is None:
            return None
        user_id = outpt[0][0]
        return user_id


    @staticmethod
    def make_folder(cursor: sqlite3.Cursor, folder_name: str, user_id: int, parent_id: int = 0):
        command = "INSERT INTO FileSystems (parent_folder, name, user_id) VALUES (?, ?, ?)"
        sql.execute_query(cursor, command, (parent_id, folder_name, user_id))

    @staticmethod
    def find_username_from_id(cursor: sqlite3.Cursor, user_id: int) -> str:
        outpt = sql.execute_select(cursor, "Users", "id", (user_id,))
        if bool(outpt):
            username = outpt[0][1]
            return username
        else:
            print("[red][bold]FIND_USERNAME_FROM_ID ERROR. INTERNAL. REPORT IMMEDIATELY[/red][/bold]")
            return ""

    @staticmethod
    def find_id_from_username(cursor: sqlite3.Cursor, username: str) -> int:
        outpt = sql.execute_select(cursor, "Users", "username", (username,))
        if bool(outpt):
            id = outpt[0][0]
            return id
        else:
            print("[red][bold]FIND_ID_FROM_USERNAME ERROR. INTERNAL. REPORT IMMEDIATELY[/red][/bold]")
            return 0


    @staticmethod
    def list_files(cursor: sqlite3.Cursor, user_id: int, location:int = 0, *, args:list[str]):
        try:
            cursor.execute("SELECT id, name FROM FileSystems WHERE user_id = ?", (user_id,))
            files = cursor.fetchall()
            for file in files:
                print(f"[green][bold]{file[1]}[/green][/bold]")
        except sqlite3.Error as e:
            print(f"[red][bold]Error listing files: {e}[/red][/bold]")
