import sqlite3
from DriveUploader.SQLCommands import SQL_Executor as sql
from rich import print
from settings import BANNED_FOLDER_NAMES

class File:
    def __init__(self, id, parent_folder, name, time_created):
        self.id = id
        self.name = name
        self.time_created = time_created

class Folder:
    def __init__(self, id, name, time_created):
        self.id = id
        self.name = name
        self.time_created = time_created
        self.children: list[Folder | File] = []

    def add_child(self, child):
        self.children.append(child)

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, index: str | int):
        if isinstance(index, str):
            for child in self.children:
                if child.name == index:
                    return child
            raise KeyError(f"Child with name '{index}' not found")
        elif isinstance(index, int):
            if index < 0 or index >= len(self.children):
                raise IndexError("Index out of range")
            return self.children[index]
        else:
            raise TypeError("Index must be a string or an integer")

    def __len__(self):
        return len(self.children)

    def __repr__(self):
        return f"Folder({self.name}, Children={self.children})"


    def add_folder(self, folders: list):
        for folder in folders:
            self.add_child(folder)

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

    # TODO: Implement the usage of passwords!
    @staticmethod
    def login(cursor: sqlite3.Cursor, login_args: list) -> int | None:
        outpt = sql.execute_select(cursor, "Users", ["username"], login_args)
        if not bool(outpt):
            return None
        if outpt[0][4] is not None:
            return None

        user_id = outpt[0][0]
        return user_id


    @staticmethod
    def make_folder(cursor: sqlite3.Cursor,  user_id: int, parent_id: int, folder_name: str, *, override=False):
        if folder_name in BANNED_FOLDER_NAMES and not override:
            print(f"[indian_red1][bold]Error: Folder name '{folder_name}' is banned.[/indian_red1][/bold]")
            return None
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
    def list_files(cursor: sqlite3.Cursor, user_id: int, *, args:list[str], main_location: int | str = 0, current_location: int = 0):
        main_location = main_location if isinstance(main_location, int) else foldername_to_id(cursor, user_id, main_location)
        return ls_folder(cursor, user_id, main_location)[0]

    @staticmethod
    def print_folder(fd: Folder):
        ptFolder(fd)

    @staticmethod
    def find_root_folder_id(cursor: sqlite3.Cursor, user_id: int) -> int | None:
        root_folder_id = sql.execute_select(cursor, "FileSystems", ["parent_folder", "user_id"], [0, user_id])
        if bool(root_folder_id):
            id = root_folder_id[0][0]
            return id
        else:
            print("[red][bold]FIND_ROOT_FOLDER_ID ERROR. INTERNAL. REPORT IMMEDIATELY[/red][/bold]")
            return None

    @staticmethod
    def find_parent_folder_id(cursor: sqlite3.Cursor, user_id: int, current_directory: int) -> int | None:
        parent_folder_id = sql.execute_select(cursor, "FileSystems", ["id", "user_id"], [current_directory, user_id])
        if bool(parent_folder_id):
            id = parent_folder_id[0][2]
            return id
        else:
            print("[red][bold]FIND_PARENT_FOLDER_ID ERROR. INTERNAL. REPORT IMMEDIATELY[/red][/bold]")
            return None

    @staticmethod
    def change_directory(cursor: sqlite3.Cursor, user_id: int, current_directory:int, new_directory:str):
        new_directory_id = foldername_to_id(cursor, user_id, new_directory, search_directory=current_directory)
        if new_directory_id == 0 and new_directory == "/":
            new_directory_id = frfid(cursor, user_id)
        elif new_directory_id == 0 and new_directory == "..":
            new_directory_id = fpfid(cursor, user_id, current_directory)

        if new_directory_id != 0:
            return new_directory_id
        else:
            print(f"[deep_pink2][italic]Directory {new_directory} not found[/italic][/deep_pink2]")

    foldername_to_id = lambda x, y, z, *, search_directory=None: foldername_to_id(x, y, z, search_directory=search_directory)
    id_to_foldername = lambda x, y, z: id_to_foldername(x, y, z)

def foldername_to_id(cursor: sqlite3.Cursor, user_id: int, folder_name: str, *, search_directory: int | None = None) -> int:
    search_args: list[int | str] = [folder_name]
    colomn_names = ["name"]
    if search_directory is not None:
        search_args.append(search_directory)
        colomn_names.append("parent_folder")
    folder_id = sql.execute_select(cursor, "FileSystems", colomn_names, search_args)
    if bool(folder_id):
        id = folder_id[0][0]
        return id
    elif folder_id is None:
        print("[red][bold]FOLDERNAME_TO_ID ERROR. INTERNAL. REPORT IMMEDIATELY[/red][/bold]")
        return 0
    else:
        return 0

frfid = lambda x, y: SQLite_Utils.find_root_folder_id(x, y)
fpfid = lambda x, y, z: SQLite_Utils.find_parent_folder_id(x, y, z)
find_root_folder_id = lambda x, y: SQLite_Utils.find_root_folder_id(x, y)

def id_to_foldername(cursor: sqlite3.Cursor, user_id: int, folder_id: int) -> str:
    folder_name = sql.execute_select(cursor, "FileSystems", "id", (folder_id,))
    if bool(folder_name):
        name = folder_name[0][3]
        return name
    elif folder_name is None:
        print("[red][bold]ID_TO_FOLDERNAME ERROR. INTERNAL. REPORT IMMEDIATELY[/red][/bold]")
        return ""
    else:
        return ""

# def id_to_folder(cursor: sqlite3.Cursor, user_id: int, folder_id: int) -> Folder:
#     folder_data = sql.execute_select(cursor, "FileSystems", "id", (folder_id,))
#     if bool(folder_data):
#         data = folder_data[0]
#         return Folder(data[0], data[3], data[4])
#     else:
#         # print("[red][bold]ID_TO_FOLDER ERROR. INTERNAL. REPORT IMMEDIATELY[/red][/bold]")
#         return Folder(0, "", "")

def ptFolder(fd: Folder, depth: int = 0) -> None:
    folder = "󰉋"
    file_item = ""
    print(f"{'  ' * depth}{folder} {fd.name}")
    for item in fd.children:
        if isinstance(item, Folder):
            ptFolder(item, depth+1)
        elif isinstance(item, File):
            print(f"{'  ' * (depth+1)}{file_item} {item.name}")

def ls_folder(cursor: sqlite3.Cursor, user_id:int, location:int = 0, depth:int = 0) -> list[Folder]:
            folders_found = sql.execute_query(cursor, "SELECT * FROM FileSystems WHERE user_id = ? AND parent_folder = ?", (user_id, location))
            manifests_folder = sql.execute_query(cursor, "SELECT * FROM Manifests WHERE user_id = ? AND location = ?", (user_id, location))
            folder_items = []

            if not folders_found:
                folders_found=[]
            if not manifests_folder:
                manifests_folder=[]

            for items in folders_found:
                if items[-1] is not None:
                    continue
                FD_Object = Folder(items[0],items[3],items[4])
                internal_folder_items = ls_folder(cursor, user_id, items[0], depth+1)
                FD_Object.add_folder(internal_folder_items)
                folder_items.append(FD_Object)

            return folder_items

            # folder = "󰉋"
            # file_item = ""
            # for items in folders_found:
            #     if items[-1] is not None:
            #         print(f"{'  ' * depth}[steel_blue1]{folder} {items[3]}[/steel_blue1]")
            #         ls_folder(cursor, user_id, items[0], depth+1)
            # for items in manifests_folder:
            #     print(f"[blue_violet]{file_item} {items[2]}[/blue_violet]")

            # return folders_found
