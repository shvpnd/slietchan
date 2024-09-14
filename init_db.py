import sqlite3

DATABASE = 'quickchan.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Drop existing tables if they exist
    cursor.execute("DROP TABLE IF EXISTS posts;")
    cursor.execute("DROP TABLE IF EXISTS boards;")
    cursor.execute("DROP TABLE IF EXISTS reply;")
    cursor.execute("DROP TABLE IF EXISTS replies;")

    # Create tables
    with open('schema.sql', 'r') as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
