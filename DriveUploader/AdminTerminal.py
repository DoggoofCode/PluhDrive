import sqlite3
from rich import print
from rich.prompt import Prompt
from DriveUploader.utils import Folder, SQLite_Utils as sqlu, HelperFunctions, TerminalCommands
import os

class Command:
    def __init__(self, arguments: list[str], flags: list[str]) -> None:
        self.args = arguments
        self.flags = flags

    @property
    def main_argument(self) -> str | None:
        return self.args[0] if self.args else None


    def _minimumArguments(self, length: int) -> bool:
        if len(self.args)-1 >= length:
            return True
        else:
            print(f"Minimum arguments not satisfied. Expected {length}, got {len(self.args)}.")
            return False

    def _maximumArguments(self, length: int) -> bool:
        if len(self.args)-1 <= length:
            return True
        else:
            print(f"Maximum arguments not satisfied. Expected {length}, got {len(self.args)-1}.")
            return False

    def EqArgs(self, min:int, max:int) -> bool:
        if self._minimumArguments(min) and self._maximumArguments(max):
            return True
        else:
            return False

    def __str__(self) -> str:
        return f"Command(args={self.args}, flags={self.flags})"



class AdminTerminal:
    def __init__(self, prefix: str, cursor: sqlite3.Cursor) -> None:
        self.input_prefix = prefix
        self.cursor: sqlite3.Cursor = cursor

    def command_processing(self, command: str) -> Command:
        argumentised: list[str] = command.lower().split()
        flags = []
        for index in range(len(argumentised)):
            if argumentised[index][0] == '-':
                flags.append(argumentised[index][1:])
                argumentised[index] = ""
        argumentised = [arg for arg in argumentised if arg]
        for index, flg in enumerate(flags):
            if len(flg) == 0:
                flags.pop(index)
            elif len(flg) > 1:
                for f in flg:
                    flags.append(f)
                flags.pop(index)
                continue

        arg = Command(argumentised, flags)

        return arg

    @property
    def login_check(self) -> bool:
        if self.USER_ID is None or self.CURRENT_DIRECTORY is None:
            print("[red][bold]Not logged in[/red][/bold]")
            return False
        return True

    def begin(self) -> None:
        print("[green]Welcome to the Admin Terminal![/green]")
        arguments: Command
        self.USER_ID = None
        self.CURRENT_DIRECTORY: int | None = None
        cursor = self.cursor
        while True:
            command: str = Prompt.ask(f"${self.input_prefix}")
            arguments: Command = self.command_processing(command)


            match arguments.main_argument:
                case "exec":
                    # No argument limit
                    sqlu.safe_execute_query(cursor, " ".join(arguments.args[1:]))
                case "pexec":
                    # No argument limit
                    try:
                        exec(" ".join(arguments.args[1:]))
                    except NameError:
                        sqlu.util_execute(cursor, " ".join(arguments.args[1:]))
                    except Exception as e:
                        print(f"[red][bold]Error[/red][/bold]: {e}")
                case "listusrs":
                    sqlu.safe_execute_query(cursor, "SELECT * FROM Users")
                case "mkusr":
                    if not arguments.EqArgs(2,2):
                        print("[red][bold]Invalid arguments[/red][/bold]")
                        continue
                    sqlu.safe_insert(cursor, "Users", ("username", "password"), arguments.args[1:])
                    new_user_id: int = HelperFunctions.find_id_from_username(cursor, arguments.args[1])
                    sqlu.make_folder(cursor, new_user_id, 0,"/", override=True)
                case "delusr_id":
                    if not arguments.EqArgs(1,1):
                        print("[red][bold]Invalid arguments[/red][/bold]")
                        continue
                    sqlu.safe_execute(cursor, "DELETE FROM Users WHERE id = ?", arguments.args[1:])
                case "login":
                    if not arguments.EqArgs(1,2):
                        print("[red][bold]Invalid arguments[/red][/bold]")
                        continue
                    self.USER_ID = TerminalCommands.login(cursor, arguments.args[1:])
                    if not self.USER_ID:
                        print("[red][bold]Invalid username or password[/red][/bold]")
                        continue
                    rt_directory = HelperFunctions.find_root_folder_id(cursor, self.USER_ID)
                    if not rt_directory:
                        print("[red][bold]Root directory not found[/red][/bold]")
                        continue
                    self.CURRENT_DIRECTORY = rt_directory

                    print(f"[blue][bold]Logged in as {HelperFunctions.find_username_from_id(cursor, self.USER_ID)}[/blue][/bold]")
                case "logout":
                    self.USER_ID = None
                    self.CURRENT_DIRECTORY = None
                case "whoami":
                    if not self.USER_ID:
                        print("[red][bold]Not logged in[/red][/bold]")
                    else:
                        print(f"[green][bold]Logged in as {HelperFunctions.find_username_from_id(cursor, self.USER_ID)}[/green][/bold]")
                case "ls":
                    if not arguments.EqArgs(0,1):
                        print("[red][bold]Invalid arguments[/red][/bold]")
                        continue
                    if not self.USER_ID:
                        print("[red][bold]Not logged in[/red][/bold]")
                        continue
                    if len(arguments.args) == 1:
                        f_list: Folder = sqlu.list_files(cursor, self.USER_ID, args=arguments.flags)
                    else:
                        f_list: Folder = sqlu.list_files(cursor, self.USER_ID, main_location=arguments.args[1], args=arguments.flags)

                    sqlu.print_folder(f_list)
                case "cd":
                    if not arguments.EqArgs(1,1):
                        print("[red][bold]Invalid arguments[/red][/bold]")
                        continue
                    if not self.USER_ID or self.CURRENT_DIRECTORY is None:
                        print("[red][bold]Not logged in[/red][/bold]")
                        continue
                    self.CURRENT_DIRECTORY
                    new_possible_directory = sqlu.change_directory(cursor, self.USER_ID, self.CURRENT_DIRECTORY, arguments.args[1])
                    if new_possible_directory is None:
                        pass
                    else:
                        self.CURRENT_DIRECTORY = new_possible_directory
                case "mkdir":
                    if not self.login_check:
                        continue
                    if not arguments.EqArgs(1,1):
                        print("[red][bold]Invalid arguments[/red][/bold]")
                        continue
                    sqlu.make_folder(cursor, self.USER_ID, self.CURRENT_DIRECTORY, arguments.args[1])
                case "mkfile":
                    if not self.login_check:
                        continue
                    if not arguments.EqArgs(1,2):
                        print("[red][bold]Invalid arguments[/red][/bold]")
                        continue
                    # path then name
                    sqlu.make_file(cursor, self.USER_ID, self.CURRENT_DIRECTORY, arguments.args[1], arguments.args[2])
                case "clear":
                    os.system('cls' if os.name == 'nt' else 'clear')
                case "exit":
                    print("[green]Exiting...[/green]")
                    break
                case "pwd":
                    if self.USER_ID is None or self.CURRENT_DIRECTORY is None:
                        print("[red][bold]Not logged in[/red][/bold]")
                        continue
                    print(f"[green][bold]{HelperFunctions.id_to_foldername(cursor, self.USER_ID, self.CURRENT_DIRECTORY)}[/green][/bold]")
                case _:
                    print(f"[red][bold]Unknown command: {arguments.main_argument}[/red][/bold]")
