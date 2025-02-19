import sqlite3

# Connect to the database (creates it if it doesn't exist)
conn = sqlite3.connect("mydb.db")
cursor = conn.cursor()

# Create the students table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    grade TEXT
);
""")

# Insert sample data
students_data = [
    ("Alice", 20, "A"),
    ("Bob", 22, "B"),
    ("Charlie", 19, "C")
]

cursor.executemany("INSERT INTO students (name, age, grade) VALUES (?, ?, ?);", students_data)

# Commit and close connection
conn.commit()
conn.close()

print("Students table created and data inserted.")
