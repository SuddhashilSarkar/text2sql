import sqlite3

# Connect to the database
conn = sqlite3.connect("mydb.db")
cursor = conn.cursor()

# Fetch and print all student records
#cursor.execute("PRAGMA table_info(students);")
cursor.execute("SELECT * FROM students;")
students = cursor.fetchall()


print("Student Records:")
for student in students:
    print(student)

# Close the connection
conn.close()
