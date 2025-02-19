import sqlite3
import csv
import datetime

# Database file
db_file = "mydb.db"
csv_file = "datafill/student_data.csv"

# Get the current year in Python (avoiding SQLite strftime error)
CURRENT_YEAR = datetime.datetime.now().year

# Connect to SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Drop the table if it already exists (to ensure the new constraints take effect)
cursor.execute("DROP TABLE IF EXISTS students;")

# Create students table with corrected CHECK constraints
cursor.execute(f"""
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER CHECK(age BETWEEN 5 AND 30),
    gender TEXT CHECK(gender IN ('Male', 'Female', 'Other')),
    grade TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT UNIQUE NOT NULL CHECK(length(phone) BETWEEN 10 AND 15),
    address TEXT NOT NULL,
    cgpa REAL CHECK(cgpa BETWEEN 0.0 AND 10.0),
    enrollment_year INTEGER CHECK(enrollment_year BETWEEN 2010 AND {CURRENT_YEAR})
);
""")

# Read CSV and insert data
with open(csv_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)  # Automatically skips the header
    data = [
        (
            row["Name"],
            int(row["Age"]),
            row["Gender"],
            row["Grade"],
            row["Email"],
            row["Phone"],
            row["Address"],
            float(row["CGPA"]),
            int(row["Enrollment Year"])
        )
        for row in reader
    ]

# Insert data with error handling
try:
    cursor.executemany("""
    INSERT INTO students (name, age, gender, grade, email, phone, address, cgpa, enrollment_year)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, data)
    conn.commit()
    print("Data inserted successfully into mydb.db")
except sqlite3.IntegrityError as e:
    print(f"Error inserting data: {e}")

# Close the connection
conn.close()
