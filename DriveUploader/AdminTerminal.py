import sqlite3
from rich import print
from rich.prompt import Prompt
from DriveUploader.utils import SQLite_Utils

class Command:
    def __init__(self, arguments: list[str], flags: list[str]) -> None:
        self.args = arguments
        self.flags = flags

    @property
    def main_argument(self) -> str | None:
        return self.args[0] if self.args else None


    def _minimumArguments(self, length: int) -> bool:
        if len(self.args) >= length:
            print("Minimum arguments satisfied.")
            return True
        else:
            print(f"Minimum arguments not satisfied. Expected {length}, got {len(self.args)}.")
            return False

    def _maximumArguments(self, length: int) -> bool:
        if len(self.args) <= length:
            print("Maximum arguments satisfied.")
            return True
        else:
            print(f"Maximum arguments not satisfied. Expected {length}, got {len(self.args)}.")
            return False

    def EqArgs(self, min:int, max:int) -> bool:
        if self._minimumArguments(min) and self._maximumArguments(max):
            print("Arguments satisfied.")
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

            match arguments.main_argument:
                case "exec":
                    # No argument limit
                    SQLite_Utils.execute_query(cursor, " ".join(arguments.args[1:]))
                case "exit":
                    print("[green]Exiting...[/green]")
                    break
                case _:
                    print(f"[red][bold]Unknown command: {arguments.main_argument}[/red][/bold]")
