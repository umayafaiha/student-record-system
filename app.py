from functools import wraps
from flask import Flask, render_template, request, redirect, session, url_for, flash
from db import get_db_connection
from werkzeug.security import check_password_hash
import datetime

app = Flask(__name__)
app.secret_key = 'fyha123'

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'username' not in session:
			return redirect(url_for('login'))
		return f(*args, **kwargs)
	return decorated_function

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'username' not in session or 'role' not in session:
                return redirect(url_for('login'))
            if session['role'] != required_role:
                return "Access Denied: You do not have permission to view this page.", 403
            return f(*args, **kwargs)
        return wrapped
    return decorator

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        con = get_db_connection()
        cursor = con.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        con.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password.'

    return render_template('login.html', error=error)
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
	return render_template('dashboard.html')

@app.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_student():
 

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        age = request.form['age']
        course = request.form['course']
        enrollment_date = request.form['enrollment_date']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO students (name, email, age, course, enrollment_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, age, course, enrollment_date))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/students')

    return render_template('add_student.html')
@app.route('/students')
@login_required

def view_students():


    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('view_students.html', students=students)
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('view_students.html', students=students)

@app.route('/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')

def edit_student(student_id):


  

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        age = request.form['age']
        course = request.form['course']
        enrollment_date = request.form['enrollment_date']

        cursor.execute(
            "UPDATE students SET name=%s, email=%s, age=%s, course=%s, enrollment_date=%s WHERE id=%s",
            (name, email, age, course, enrollment_date, student_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('view_students'))

    cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()

    if student and isinstance(student['enrollment_date'], datetime.date):
        student['enrollment_date'] = student['enrollment_date'].strftime('%Y-%m-%d')

    return render_template('edit_student.html', student=student)
@app.route('/delete/<int:student_id>')
@login_required
@role_required('admin')
def delete_student(student_id):
   

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/students')

# --------- Attendance Routes ---------

@app.route('/attendance')
@login_required

def view_attendance():
  

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, s.name, a.date, a.status 
        FROM attendance a 
	JOIN students s ON a.student_id = s.id
        ORDER BY a.id ASC
    """)
    attendance_records = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('view_attendance.html', attendance=attendance_records)
@app.route('/attendance/add', methods=['GET', 'POST'])
@login_required

def add_attendance():
    

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    if request.method == 'POST':
        student_id = request.form['student_id']
        date = request.form['date']
        status = request.form['status']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO attendance (student_id, date, status) VALUES (%s, %s, %s)",
            (student_id, date, status)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/attendance')

    return render_template('add_attendance.html', students=students)
@app.route('/attendance/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_attendance(id):


    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        student_id = request.form['student_id']
        date = request.form['date']
        status = request.form['status']

        cursor.execute("""
            UPDATE attendance SET student_id=%s, date=%s, status=%s WHERE id=%s
        """, (student_id, date, status, id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/attendance')

    # GET request: fetch current attendance data
    cursor.execute("SELECT * FROM attendance WHERE id=%s", (id,))
    attendance = cursor.fetchone()

    cursor.execute("SELECT id, name FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('edit_attendance.html', attendance=attendance, students=students)

@app.route('/attendance/delete/<int:id>', methods=['POST'])
@login_required

def delete_attendance(id):
    

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/attendance')

# Route to add grades
@app.route('/add_grade', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
def add_grade():
   

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        student_id = request.form['student']
        subject = request.form['subject']
        grade = request.form['grade']

        cursor.execute("INSERT INTO grades (student_id, subject, grade) VALUES (%s, %s, %s)", (student_id, subject, grade))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/add_grade')  # Or redirect to another page if needed

    # Fetch all students to populate dropdown
    cursor.execute("SELECT id, name FROM students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('add_grade.html', students=students)# Route to view all grades
@app.route('/grades')
@login_required

def view_grades():
  

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT g.id, s.name, g.subject, g.grade
        FROM grades g
        JOIN students s ON g.student_id = s.id
    ''')
    grades = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('view_grades.html', grades=grades)
#--- Edit a grade ---
@app.route('/edit_grade/<int:grade_id>', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
def edit_grade(grade_id):


    conn = get_db_connection()
    cursor = conn.cursor()
    # Fetch students for dropdown
    cursor.execute("SELECT id, name FROM students ORDER BY name")
    students = cursor.fetchall()

    if request.method == 'POST':
        student_id = request.form['student_id']
        subject = request.form['subject']
        grade = request.form['grade']

        cursor.execute("""
            UPDATE grades 
            SET student_id=%s, subject=%s, grade=%s 
            WHERE id=%s
        """, (student_id, subject, grade, grade_id))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('view_grades'))

    # GET request: fetch grade details to fill form
    cursor.execute("SELECT student_id, subject, grade FROM grades WHERE id=%s", (grade_id,))
    grade_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if grade_data is None:
        return "Grade not found!", 404

    return render_template('edit_grade.html', grade=grade_data, students=students, grade_id=grade_id)

#---Deletegrade---
@app.route('/delete_grade/<int:grade_id>', methods=['POST'])
@login_required
@role_required('teacher')
def delete_grade(grade_id):
   

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM grades WHERE id=%s", (grade_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('view_grades'))

if __name__ == '__main__':
	app.run(debug=True)