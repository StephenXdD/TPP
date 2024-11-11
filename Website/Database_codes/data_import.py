import sqlite3
import pandas as pd

# Load Excel data
file_path = r"C:\Users\Dev Joshi\Desktop\STATS.xlsx"
try:
    data = pd.read_excel(file_path)
except FileNotFoundError:
    print(f"Error: The file {file_path} was not found.")
    exit()

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('past_papers.db')
cursor = conn.cursor()

# Insert data into the database
insert_query = """
INSERT INTO past_papers (subject_name, subject_code, topic, sub_topic, paper_number, paper_variant, 
                         variant, difficulty, year, marks, question_number)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

# Iterate over the rows in the DataFrame and insert them into the database
for _, row in data.iterrows():
    cursor.execute(insert_query, (
        row['Subject Name'], row['Subject Code'], row['Topic'], row['Sub topic'], row['Paper Number'],
        row['Paper Variant'], row['Variant'], row['Difficulty'], row['Year'], row['Marks'], row['Question Number']
    ))

# Commit the transaction and close the connection
conn.commit()
conn.close()
