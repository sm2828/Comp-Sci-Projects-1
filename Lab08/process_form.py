#!/usr/bin/env python3
import cgi
import sqlite3

# Connect to the database
conn = sqlite3.connect('student_database.db')
cursor = conn.cursor()

# Get the form data
form = cgi.FieldStorage()
name = form.getvalue('name')
midterm_exam1 = float(form.getvalue('midterm_exam1'))
midterm_exam2 = float(form.getvalue('midterm_exam2'))
final_exam = float(form.getvalue('final_exam'))

# Calculate the average score
average_score = (midterm_exam1 + midterm_exam2 + 2 * final_exam) / 4

# Insert the student record into the database
cursor.execute("INSERT INTO student_grades (name, midterm_exam1, midterm_exam2, final_exam) VALUES (?, ?, ?, ?)",
               (name, midterm_exam1, midterm_exam2, final_exam))
conn.commit()

# Fetch all records from the database
cursor.execute("SELECT name, ((midterm_exam1 + midterm_exam2 + 2 * final_exam) / 4) as average_score FROM student_grades")
records = cursor.fetchall()

# Close the database connection
conn.close()

# Print the HTML response
print("Content-type: text/html\n")
print("<html><head><title>Student Grades</title></head><body>")
print("<h1>Student Grades Database</h1>")
print("<form action='process_form.py' method='post'>")
print("<label for='name'>Student Name:</label>")
print("<input type='text' name='name' required><br>")
print("<label for='midterm_exam1'>Midterm Exam 1:</label>")
print("<input type='number' name='midterm_exam1' required><br>")
print("<label for='midterm_exam2'>Midterm Exam 2:</label>")
print("<input type='number' name='midterm_exam2' required><br>")
print("<label for='final_exam'>Final Exam:</label>")
print("<input type='number' name='final_exam' required><br>")
print("<input type='submit' value='Add Student'>")
print("</form>")

print("<h2>Student Records</h2>")
print("<table border='1'>")
print("<tr><th>Student Name</th><th>Average Score</th><th>Action</th></tr>")
for record in records:
    print("<tr>")
    print("<td>{}</td>".format(record[0]))
    print("<td>{:.2f}</td>".format(record[1]))
    print("<td><a href='#'>Delete</a></td>")  # Add the delete link here
    print("</tr>")
print("</table>")
print("</body></html>")
