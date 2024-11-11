import sqlite3

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = sqlite3.connect(db_file)
    return conn

def create_past_papers_table(conn):
    """Create the past_papers table in the database."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS past_papers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Subject_name TEXT NOT NULL,
        Subject_code INTEGER NOT NULL,
        Topic TEXT NOT NULL,
        Sub_topic TEXT,
        Paper_number INTEGER NOT NULL,
        Paper_variant TEXT NOT NULL,
        Variant TEXT NOT NULL,
        Difficulty TEXT NOT NULL,
        Year INTEGER NOT NULL,
        Marks INTEGER NOT NULL,
        Question_Number TEXT,
        Content TEXT
    );
    """
    conn.execute(create_table_sql)
    conn.commit()

def main():
    # Specify the database file name
    database = 'past_papers.db'

    # Create a database connection
    conn = create_connection(database)

    # Create the past_papers table
    create_past_papers_table(conn)

    # Close the database connection
    conn.close()
    print("Database and table created successfully.")

if __name__ == "__main__":
    main()
