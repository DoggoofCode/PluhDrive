import sqlite3
from rich import print
from rich.prompt import Prompt
from DriveUploader.utils import SQLite_Utils as sqlu

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
            print(f"Maximum arguments not satisfied. Expected {length}, got {len(self.args)}.")
            return False

    def EqArgs(self, min:int, max:int) -> bool:
        if self._minimumArguments(min) and self._maximumArguments(max):
            return True
        else:
            return False

    def __str__(self) -> str:
        return f"Command(args={self.args}, flags={self.flags})"



class AdminTerminal:
    def __init__(self, prefix: str) -> None:
        self.input_prefix = prefix

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

    def begin(self, cursor: sqlite3.Cursor) -> None:
        print("[green]Welcome to the Admin Terminal![/green]")
        arguments: Command
        while True:
            command: str = Prompt.ask(f"${self.input_prefix}")
            arguments: Command = self.command_processing(command)
            USER_ID = None

            match arguments.main_argument:
                case "exec":
                    # No argument limit
                    sqlu.execute_query(cursor, " ".join(arguments.args[1:]))
                case "listusrs":
                    sqlu.execute_query(cursor, "SELECT * FROM users")
                case "mkusr":
                    if not arguments.EqArgs(2,2):
                        print("[red][bold]Invalid arguments[/red][/bold]")
                        continue
                    sqlu.safe_insert(cursor, "Users", ("username", "password"), arguments.args[1:])
                    new_user_id: int = sqlu.find_id_from_username(cursor, arguments.args[1])
                    sqlu.make_folder(cursor, "Users", new_user_id)
                case "delusr_id":
                    if not arguments.EqArgs(1,1):
                        print("[red][bold]Invalid arguments[/red][/bold]")
                        continue
                    sqlu.safe_execute(cursor, "DELETE FROM Users WHERE id = ?", arguments.args[1:])
                case "login":
                    if not arguments.EqArgs(1,2):
                        print("[red][bold]Invalid arguments[/red][/bold]")
                        continue
                    USER_ID = sqlu.login(cursor, arguments.args[1:])
                case "exit":
                    print("[green]Exiting...[/green]")
                    break
                case _:
                    print(f"[red][bold]Unknown command: {arguments.main_argument}[/red][/bold]")
