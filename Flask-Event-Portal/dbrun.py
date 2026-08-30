import sqlite3

def createDatabase(dbname="portal.db"):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()

    c.execute("PRAGMA foreign_keys = ON;")

    c.execute("""
        CREATE TABLE IF NOT EXISTS User(
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name     TEXT NOT NULL,
            email    TEXT NOT NULL,
            isAdmin  INTEGER NOT NULL CHECK(isAdmin IN (0,1))
        );
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS Society(
            societyID INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL UNIQUE
        );
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS Event(
            eventID     INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL UNIQUE,
            timeDate    TEXT NOT NULL,
            description TEXT NOT NULL,
            entryPrice  REAL NOT NULL,
            username    TEXT NOT NULL,
            FOREIGN KEY(username) REFERENCES User(username)
        );
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS involves(
            eventID   INTEGER NOT NULL,
            societyID INTEGER NOT NULL,
            PRIMARY KEY(eventID, societyID),
            FOREIGN KEY(eventID) REFERENCES Event(eventID) ON DELETE CASCADE,
            FOREIGN KEY(societyID) REFERENCES Society(societyID) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    createDatabase("portal.db")
