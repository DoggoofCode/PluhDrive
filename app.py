from settings import DATABASE_LOCATION
import sqlite3

def main() -> None:
    connection = sqlite3.connect(DATABASE_LOCATION)
    cursor = connection.cursor()


if __name__ == "__main__":
    main()
