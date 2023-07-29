import sqlite3

# Connect to the database (create it if it doesn't exist)
conn = sqlite3.connect('student_database.db')
cursor = conn.cursor()

# Create a table to store student grades
cursor.execute('''CREATE TABLE IF NOT EXISTS student_grades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    midterm_exam1 REAL,
                    midterm_exam2 REAL,
                    final_exam REAL
                )''')

# Save the changes and close the connection
conn.commit()
conn.close()
