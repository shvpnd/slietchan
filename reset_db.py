import sqlite3

DATABASE = 'quickchan.db'

def clear_data():
    # Connect to the database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Delete all records from each table
    cursor.execute("DELETE FROM posts")
    cursor.execute("DELETE FROM replies")
    cursor.execute("DELETE FROM boards")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    clear_data()
    print("All data cleared from the database.")