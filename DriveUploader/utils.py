import sqlite3
from DriveUploader.SQLCommands import SQL_Executor as sql
from rich import print
from settings import BANNED_FOLDER_NAMES, BANNED_FILE_NAMES, FileStoreLocation, LOCATION
from hashlib import sha256
ID_Type = int | None
SQC = sqlite3.Cursor

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

class HelperFunctions:
    @staticmethod
    def find_similar_folder(cursor: SQC, folder_name: str, parent_id: int) -> bool:
        outpt = sql.execute_select(cursor, "FileSystems", ["name", "parent_folder"], [folder_name, parent_id])
        if not bool(outpt):
            return False
        for row in outpt:
            if row[3] == folder_name:
                return True
        return False

    @staticmethod
    def find_username_from_id(cursor: SQC, user_id: int) -> str:
        outpt = sql.execute_select(cursor, "Users", "id", (user_id,))
        if bool(outpt):
            username = outpt[0][1]
            return username
        else:
            print("[red][bold]FIND_USERNAME_FROM_ID ERROR. INTERNAL. REPORT IMMEDIATELY[/red][/bold]")
            return ""

    @staticmethod
    def find_id_from_username(cursor: SQC, username: str) -> int:
        outpt = sql.execute_select(cursor, "Users", "username", (username,))
        if bool(outpt):
            id = outpt[0][0]
            return id
        else:
            print("[red][bold]FIND_ID_FROM_USERNAME ERROR. INTERNAL. REPORT IMMEDIATELY[/red][/bold]")
            return 0

    @staticmethod
    def find_root_folder_id(cursor: SQC, user_id: int) -> ID_Type:
        root_folder_id = sql.execute_select(cursor, "FileSystems", ["parent_folder", "user_id"], [0, user_id])
        if bool(root_folder_id):
            id = root_folder_id[0][0]
            return id
        else:
            print("[red][bold]FIND_ROOT_FOLDER_ID ERROR. INTERNAL. REPORT IMMEDIATELY[/red][/bold]")
            return None

    @staticmethod
    def find_parent_folder_id(cursor: SQC, user_id: int, folder_id: int) -> ID_Type:
        parent_folder_id = sql.execute_select(cursor, "FileSystems", ["parent_folder", "user_id"], [folder_id, user_id])
        if bool(parent_folder_id):
            id = parent_folder_id[0][0]
            return id
        else:
            print("[red][bold]FIND_PARENT_FOLDER_ID ERROR. INTERNAL. REPORT IMMEDIATELY[/red][/bold]")
            return None

    @staticmethod
    def foldername_to_id(cursor: SQC, user_id: int, folder_name: str, *, search_directory: ID_Type = None) -> int:
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

    @staticmethod
    def id_to_foldername(cursor: SQC, user_id: int, folder_id: int) -> str:
        folder_name = sql.execute_select(cursor, "FileSystems", "id", (folder_id,))
        if bool(folder_name):
            name = folder_name[0][3]
            return name
        elif folder_name is None:
            print("[red][bold]ID_TO_FOLDERNAME ERROR. INTERNAL. REPORT IMMEDIATELY[/red][/bold]")
            return ""
        else:
            return ""

    @staticmethod
    def walk_folder(cursor: SQC, user_id:int, location:int = 0, depth:int = 0) -> list[Folder]:
        folders_found = sql.execute_query(cursor, "SELECT * FROM FileSystems WHERE user_id = ? AND parent_folder = ?", (user_id, location))
        manifests_found = sql.execute_query(cursor, "SELECT * FROM Manifests WHERE user_id = ? AND location = ?", (user_id, location))
        folder_items = []

        if not folders_found:
            folders_found=[]
        if not manifests_found:
            manifests_found=[]

        for items in folders_found:
            if items[-1] is not None:
                continue
            FD_Object = Folder(items[0],items[3],items[4])
            internal_folder_items = HelperFunctions.walk_folder(cursor, user_id, items[0], depth+1)
            FD_Object.add_folder(internal_folder_items)
            folder_items.append(FD_Object)

        for items in manifests_found:
            if items[-4] is not None:
                continue
            FileObject = File(items[0],items[-3],items[2],items[4])
            folder_items.append(FileObject)

        return folder_items

    @staticmethod
    def store_file(path:str) -> str:
        with open(LOCATION + path, "rb") as file:
            contents = file.read()
        hash = sha256(contents).hexdigest()
        with open(FileStoreLocation + hash + ".str", "wb") as file:
            file.write(contents)
        return hash


class TerminalCommands:
    # TODO: Implement the usage of passwords!
    @staticmethod
    def login(cursor: SQC, login_args: list) -> ID_Type:
        outpt = sql.execute_select(cursor, "Users", ["username"], login_args)
        if not bool(outpt):
            return None
        if outpt[0][4] is not None:
            return None

        user_id = outpt[0][0]
        return user_id

    @staticmethod
    def print_folder_contents(fd: Folder, depth: int = 0) -> None:
        folder = "󰉋"
        file_item = ""
        print(f"{'  ' * depth}{folder} {fd.name}")
        for item in fd.children:
            if isinstance(item, Folder):
                TerminalCommands.print_folder_contents(item, depth+1)
            elif isinstance(item, File):
                print(f"{'  ' * (depth+1)}{file_item} {item.name}")

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
                    description TEXT,
                    time_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    time_deleted TIMESTAMP DEFAULT NULL,
                    location INTEGER NOT NULL,
                    original_file_name VARCHAR(50) NOT NULL,
                    hash VARCHAR(64),
                    FOREIGN KEY (user_id) REFERENCES Users(id),
                    FOREIGN KEY (location) REFERENCES FileSystems(id)
                );
                """)

        cursor.connection.commit()

    @staticmethod
    def safe_execute_query(cursor: SQC, query: str):
        command_output = sql.execute_query(cursor, query)
        print(f"Command Output: {command_output}")
        return command_output

    @staticmethod
    def safe_execute(cursor: SQC, query: str, values: list[str]):
        command_output = []
        command_output = sql.execute_query(cursor, query, values)
        return command_output

    @staticmethod
    def safe_insert(cursor: SQC, table_name: str, item_names: list | tuple, values: list | tuple):
        command = f"INSERT INTO {table_name} ({', '.join(item_names)}) VALUES ({', '.join(['?'] * len(values))})"
        sql.execute_query(cursor, command, values)

    @staticmethod
    def util_execute(cursor: SQC, cmd:str) -> None:
        try:
            m = eval(cmd)
            print(m)
        except Exception as e:
            print(f"[red][bold]Error[/red][/bold]: {e}")

    @staticmethod
    def make_folder(cursor: SQC,  user_id: ID_Type, parent_id: ID_Type, folder_name: str, *, override=False):
        if user_id is None or parent_id is None:
            print("[indian_red1][bold]Error: Internal.[/indian_red1][/bold]")
            return None
        if folder_name in BANNED_FOLDER_NAMES and not override:
            print(f"[indian_red1][bold]Error: Folder name '{folder_name}' is banned.[/indian_red1][/bold]")
            return None

        if HelperFunctions.find_similar_folder(cursor, folder_name, parent_id):
            print(f"[indian_red1][bold]Error: Folder '{folder_name}' already exists.[/indian_red1][/bold]")
            return None

        command = "INSERT INTO FileSystems (parent_folder, name, user_id) VALUES (?, ?, ?)"
        sql.execute_query(cursor, command, (parent_id, folder_name, user_id))

    @staticmethod
    def make_file(cursor: SQC, user_id: ID_Type, parent_id: ID_Type, file_name: str, path:str, description: str = "") -> None:
        if user_id is None or parent_id is None:
            print("[indian_red1][bold]Error: Internal.[/indian_red1][/bold]")
            return None
        if file_name in BANNED_FILE_NAMES:
            print(f"[indian_red1][bold]Error: File name '{file_name}' is banned.[/indian_red1][/bold]")
            return None
        hash_generated = HelperFunctions.store_file(path)
        command = "INSERT INTO Manifests (location, name, user_id, description, hash, original_file_name) VALUES (?, ?, ?, ?, ?, ?)"
        sql.execute_query(cursor, command, (parent_id, file_name, user_id, description, hash_generated, path.split("/")[-1]))

    @staticmethod
    def list_files(cursor: SQC, user_id: int, *, args:list[str], main_location: int | str = 0, current_location: int = 0):
        main_location = main_location if isinstance(main_location, int) else HelperFunctions.foldername_to_id(cursor, user_id, main_location)
        return HelperFunctions.walk_folder(cursor, user_id, main_location)[0]

    @staticmethod
    def print_folder(fd: Folder):
        TerminalCommands.print_folder_contents(fd)

    @staticmethod
    def change_directory(cursor: SQC, user_id: int, current_directory:int, new_directory:str):
        new_directory_id = HelperFunctions.foldername_to_id(cursor, user_id, new_directory, search_directory=current_directory)
        if new_directory_id == 0 and new_directory == "/":
            new_directory_id = HelperFunctions.find_root_folder_id(cursor, user_id)
        elif new_directory_id == 0 and new_directory == "..":
            new_directory_id = HelperFunctions.find_parent_folder_id(cursor, user_id, current_directory)


        if new_directory_id != 0:
            return new_directory_id
        else:
            print(f"[deep_pink2][italic]Directory {new_directory} not found[/italic][/deep_pink2]")
