import sqlite3
from rich import print
SQLD = str | int | float | bool
TVals = tuple[SQLD]
TVals2 = tuple[SQLD, SQLD]
TVals3 = tuple[SQLD, SQLD, SQLD]
P3VALS = list[SQLD] | TVals | TVals2 | TVals3 | None | list[str] | list


class SQL_Executor:
    @staticmethod
    def execute_query(cursor: sqlite3.Cursor, query: str, args: P3VALS = None):
        try:
            if args is None:
                cursor.execute(query)
            else:
                cursor.execute(query, args)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[red][bold]Error executing query: {e}[/red][/bold]")
            return None
        finally:
            cursor.connection.commit()

    @staticmethod
    def execute_select(cursor: sqlite3.Cursor, table: str, column: str | list[str], value: P3VALS = None):
        try:
            if value is None:
                cursor.execute(f"SELECT * FROM {table} WHERE {column} IS NULL")
            elif isinstance(value, list):
                if not isinstance(column, list):
                    print(f"[red][bold]Could not execute query, wrong input type: {type(column)}[/red][/bold]")
                elif len(column) != len(value):
                    print(f"[red][bold]Could not execute query, wrong input length: {type(value)}[/red][/bold]")
                    return None
                else:
                    conditionals = [f"{m} = ?" for m in column]
                    cursor.execute(f"SELECT * FROM {table} WHERE {' AND '.join(conditionals)}", value)
            elif isinstance(value, tuple):
                cursor.execute(f"SELECT * FROM {table} WHERE {column} = ?", value)
            else:
                print(f"[red][bold]Could not execute query, wrong input type: {type(value)}[/red][/bold]")
                return None
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[red][bold]Error executing query: {e}[/red][/bold]")
            return None
        finally:
            cursor.connection.commit()


    @staticmethod
    def execute_update(cursor: sqlite3.Cursor, table: str, column: str, value: P3VALS = None):
        try:
            if value is None:
                cursor.execute(f"UPDATE {table} SET {column} = NULL")
            elif isinstance(value, list):
                cursor.execute(f"UPDATE {table} SET {column} = ? WHERE id IN ({', '.join(['?'] * len(value))})", value)
            elif isinstance(value, tuple):
                cursor.execute(f"UPDATE {table} SET {column} = ?", value)
            else:
                print(f"[red][bold]Could not execute query, wrong input type: {type(value)}[/red][/bold]")
                return None
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[red][bold]Error executing query: {e}[/red][/bold]")
            return None
        finally:
            cursor.connection.commit()


    @staticmethod
    def execute_delete(cursor: sqlite3.Cursor, table: str, column: str, value: P3VALS = None):
        try:
            if value is None:
                cursor.execute(f"DELETE FROM {table} WHERE {column} IS NULL")
            elif isinstance(value, list):
                cursor.execute(f"DELETE FROM {table} WHERE {column} IN ({', '.join(['?'] * len(value))})", value)
            elif isinstance(value, tuple):
                cursor.execute(f"DELETE FROM {table} WHERE {column} = ?", value)
            else:
                print(f"[red][bold]Could not execute query, wrong input type: {type(value)}[/red][/bold]")
                return None
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[red][bold]Error executing query: {e}[/red][/bold]")
            return None
        finally:
            cursor.connection.commit()
