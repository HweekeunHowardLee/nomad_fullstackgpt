import sqlite3
import os

# Define the database file name
db_file = "movies.sqlite"

# Check if the database file already exists and delete it to start fresh
if os.path.exists(db_file):
    os.remove(db_file)
    print(f"Removed existing database file: {db_file}")

# Connect to the SQLite database
# The file will be created if it doesn't exist
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# --- Create Tables ---
# Note: These tables are what the LangChain agent was looking for based on your logs.
# The table schemas are a common way to organize movie data.

# Create the 'movies' table
cursor.execute('''
CREATE TABLE movies (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    budget REAL,
    votes REAL
);
''')

# Create the 'directors' table
cursor.execute('''
CREATE TABLE directors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
''')

# Create the 'movie_direction' table to link movies and directors
# This is a many-to-many relationship table.
cursor.execute('''
CREATE TABLE movie_direction (
    movie_id INTEGER,
    director_id INTEGER,
    PRIMARY KEY (movie_id, director_id),
    FOREIGN KEY (movie_id) REFERENCES movies(id),
    FOREIGN KEY (director_id) REFERENCES directors(id)
);
''')

print("Tables created successfully.")

# --- Insert Sample Data ---

# Insert data into 'movies' table
movies_data = [
    (1, 'Inception', 160000000.0, 20120),
    (2, 'The Dark Knight', 185000000.0, 26900),
    (3, 'Interstellar', 165000000.0, 20380),
    (4, 'The Matrix', 63000000.0, 22100),
    (5, 'The Godfather', 6000000.0, 19500)
]
cursor.executemany("INSERT INTO movies (id, title, budget, votes) VALUES (?, ?, ?, ?)", movies_data)

# Insert data into 'directors' table
directors_data = [
    (1, 'Christopher Nolan'),
    (2, 'Lana Wachowski'),
    (3, 'Lilly Wachowski'),
    (4, 'Francis Ford Coppola')
]
cursor.executemany("INSERT INTO directors (id, name) VALUES (?, ?)", directors_data)

# Insert data into 'movie_direction' table
movie_direction_data = [
    (1, 1), # Inception by Christopher Nolan
    (2, 1), # The Dark Knight by Christopher Nolan
    (3, 1), # Interstellar by Christopher Nolan
    (4, 2), # The Matrix by Lana Wachowski
    (4, 3), # The Matrix by Lilly Wachowski
    (5, 4)  # The Godfather by Francis Ford Coppola
]
cursor.executemany("INSERT INTO movie_direction (movie_id, director_id) VALUES (?, ?)", movie_direction_data)

print("Sample data inserted successfully.")

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database setup complete.")