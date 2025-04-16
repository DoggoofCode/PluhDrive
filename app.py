from settings import DATABASE_LOCATION
import sqlite3
from DriveUploader import AdminTerminal, SQLite_Utils

def main() -> None:
    connection = sqlite3.connect(DATABASE_LOCATION)
    cursor = connection.cursor()
    SQLite_Utils.check_table_integrity(cursor)

    AdminTerminal("AdminTerminal", cursor).begin()

    # close connection
    connection.close()




if __name__ == "__main__":
    main()
