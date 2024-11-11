import sqlite3

def create_connection(db_file):
    """Create a database connection to the SQLite database."""
    conn = sqlite3.connect(db_file)
    return conn

def drop_past_papers_table(conn):
    """Drop the past_papers table from the database."""
    query = "DROP TABLE IF EXISTS past_papers"
    conn.execute(query)
    conn.commit()

def main():
    conn = create_connection('past_papers.db')
    
    # Drop the past_papers table
    drop_past_papers_table(conn)

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()
