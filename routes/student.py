from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db import get_connection
import re

# ==================================================
# Student Management Routes
# Handles CRUD operations for Student
# ==================================================

student_bp = Blueprint('student', __name__)

# Display all students and search
@student_bp.route('/students')
def list_students():

    if session.get("role") != "AcademicStaff":
        flash("Bạn không có quyền thực hiện chức năng này.", "danger")
        return redirect(url_for("auth.home"))
    
    q = request.args.get('q', '').strip()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    if q:
        cursor.execute("""
            SELECT student_id, class_id, user_id, full_name, gender, date_of_birth, address, phone, email, department FROM students
            WHERE student_id LIKE %s OR full_name LIKE %s
               OR email LIKE %s OR department LIKE %s OR phone LIKE %s
            ORDER BY student_id
        """, (f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%'))
    else:
        cursor.execute("SELECT student_id, class_id, user_id, full_name, gender, date_of_birth, address, phone, email, department FROM students ORDER BY student_id")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('students/list.html', students=students, q=q)

# Add a new student
@student_bp.route('/students/add', methods=['GET', 'POST'])
def add_student():

    if session.get("role") != "AcademicStaff":
        flash("Bạn không có quyền thực hiện chức năng này.", "danger")
        return redirect(url_for("auth.home"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Load available student accounts
    cursor.execute("""
            SELECT user_id, username
            FROM users
            WHERE role='Student'
            AND user_id NOT IN (
                SELECT user_id FROM students
            )
            ORDER BY user_id
        """)
    users = cursor.fetchall()

    # Load available class_sections
    cursor.execute("""
            SELECT class_id, class_name
            FROM class_sections
            ORDER BY class_name
        """)
    classes = cursor.fetchall()
    if request.method == 'POST':
        class_id = request.form.get('class_id', '').strip() or None
        user_id = request.form.get('user_id', '').strip()
        student_id = request.form.get('student_id', '').strip()
        full_name  = request.form.get('full_name', '').strip()
        gender     = request.form.get('gender', '').strip()
        dob        = request.form.get('date_of_birth', '').strip()
        address    = request.form.get('address', '').strip()
        phone      = request.form.get('phone', '').strip()
        email      = request.form.get('email', '').strip() or None
        department = request.form.get('department', '').strip()

        # Kiểm tra các trường bắt buộc
        if not student_id or not user_id or not full_name or not gender or not dob:
            flash("Vui lòng điền đầy đủ các trường bắt buộc (*).", "danger")
            return render_template("students/add.html", users=users, classes=classes)

        # Student ID phải có dạng S001
        if not re.fullmatch(r"S\d{3}", student_id):
            flash("Student ID phải có định dạng S001.", "danger")
            return render_template("students/add.html", users=users, classes=classes)

        # Email (nếu có nhập)
        if email and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Email không đúng định dạng.", "danger")
            return render_template("students/add.html", users=users, classes=classes)

        # Phone (nếu có nhập)
        if phone and not re.fullmatch(r"\d{10}", phone):
            flash("Số điện thoại phải gồm đúng 10 chữ số.", "danger")
            return render_template("students/add.html", users=users, classes=classes)
                 
        # Kiểm tra Student ID
        cursor.execute(
            "SELECT student_id FROM students WHERE student_id=%s",
            (student_id,)
        )

        if cursor.fetchone():
            flash("Student ID đã tồn tại.", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for("student.add_student"))

        # Kiểm tra Email
        if email:
            cursor.execute(
                "SELECT student_id FROM students WHERE email=%s",
                (email,)
            )

            if cursor.fetchone():
                flash("Email đã tồn tại.", "danger")
                cursor.close()
                conn.close()
                return redirect(url_for("student.add_student"))
        # Kiểm tra số điện thoại  
        if phone:
            cursor.execute("""
                SELECT student_id
                FROM students
                WHERE phone=%s
            """, (phone,))

            if cursor.fetchone():
                flash("Số điện thoại đã tồn tại.", "danger")
                cursor.close()
                conn.close()
                return redirect(url_for("student.add_student"))
            
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO students
                    (student_id, class_id, user_id, full_name, gender, date_of_birth, address, phone, email, department)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (student_id, class_id, user_id, full_name, gender, dob, address, phone, email, department))
            conn.commit()
            flash(f'Thêm sinh viên {full_name} thành công!', 'success')
            return redirect(url_for('student.list_students'))
        except Exception as e:
            conn.rollback()
            flash(f"Lỗi hệ thống: {str(e)}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template('students/add.html', users=users, classes=classes)

# View student details
@student_bp.route('/students/<student_id>')
def view_student(student_id):

    if session.get("role") != "AcademicStaff":
        flash("Bạn không có quyền thực hiện chức năng này.", "danger")
        return redirect(url_for("auth.home"))
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT student_id, class_id, user_id, full_name, gender, date_of_birth, address, phone, email, department FROM students WHERE student_id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()
    if not student:
        flash('Không tìm thấy sinh viên.', 'danger')
        return redirect(url_for('student.list_students'))
    return render_template('students/view.html', student=student)

# Update student information
@student_bp.route('/students/<student_id>/edit', methods=['GET', 'POST'])
def edit_student(student_id):

    if session.get("role") != "AcademicStaff":
        flash("Bạn không có quyền thực hiện chức năng này.", "danger")
        return redirect(url_for("auth.home"))
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT student_id, class_id, user_id, full_name, gender, date_of_birth, address, phone, email, department FROM students WHERE student_id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.execute("""
            SELECT class_id, class_name
            FROM class_sections
            ORDER BY class_name
        """)
    classes = cursor.fetchall()
    cursor.close()
    conn.close()

    if not student:
        flash('Không tìm thấy sinh viên.', 'danger')
        return redirect(url_for('student.list_students'))
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        class_id = request.form.get('class_id', '').strip() or None
        full_name  = request.form.get('full_name', '').strip()
        gender     = request.form.get('gender', '').strip()
        dob        = request.form.get('date_of_birth', '').strip()
        address    = request.form.get('address', '').strip()
        phone      = request.form.get('phone', '').strip()
        email      = request.form.get('email', '').strip() or None
        department = request.form.get('department', '').strip()

        # Kiểm tra các trường bắt buộc
        if not full_name or not gender or not dob:
            flash("Vui lòng điền đầy đủ các trường bắt buộc (*).", "danger")
            return render_template(
                "students/edit.html",
                student=student,
                classes=classes
            )

        # Email (nếu có nhập)
        if email and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Email không đúng định dạng.", "danger")
            return render_template(
                    "students/edit.html",
                    student=student,
                    classes=classes
                )

        # Phone (nếu có nhập)
        if phone and not re.fullmatch(r"\d{10}", phone):
            flash("Số điện thoại phải gồm đúng 10 chữ số.", "danger")
            return render_template(
                    "students/edit.html",
                    student=student,
                    classes=classes
                )

        # Kiểm tra Email
        if email:
            cursor.execute(
                "SELECT student_id FROM students WHERE email=%s AND student_id<>%s ",
                (email, student_id)
            )

            if cursor.fetchone():
                flash("Email đã tồn tại.", "danger")
                cursor.close()
                conn.close()
                return render_template("students/edit.html", student=student, classes=classes)
        # Kiểm tra số điện thoại  
        if phone:
            cursor.execute("""
                SELECT student_id
                FROM students
                WHERE phone=%s
                AND student_id<>%s""", (phone,student_id))

            if cursor.fetchone():
                flash("Số điện thoại đã tồn tại.", "danger")
                cursor.close()
                conn.close()
                return render_template(
                    "students/edit.html",
                    student=student,
                    classes=classes
                )

        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE students
                SET class_id=%s,full_name=%s, gender=%s, date_of_birth=%s,
                    address=%s, phone=%s, email=%s, department=%s
                WHERE student_id=%s
            """, (class_id, full_name, gender, dob, address, phone, email, department, student_id))
            conn.commit()
            flash(f'Cập nhật sinh viên {full_name} thành công!', 'success')
            return redirect(url_for('student.view_student', student_id=student_id))
        except Exception as e:
            conn.rollback()
            flash(f"Lỗi hệ thống: {str(e)}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template('students/edit.html', student=student, classes=classes)

# Delete a student
@student_bp.route('/students/<student_id>/delete', methods=['POST'])
def delete_student(student_id):

    if session.get("role") != "AcademicStaff":
        flash("Bạn không có quyền thực hiện chức năng này.", "danger")
        return redirect(url_for("auth.home"))
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT full_name FROM students WHERE student_id = %s", (student_id,))
    student = cursor.fetchone()
    if student:
         try:
            cursor.execute(
            "DELETE FROM students WHERE student_id=%s",(student_id,))
            conn.commit()
            flash(
            f'Đã xoá sinh viên {student["full_name"]}.','warning')

         except Exception as e:
            conn.rollback()
            flash(f"Lỗi hệ thống: {str(e)}", "danger")
    else:
        flash('Không tìm thấy sinh viên.', 'danger')
    cursor.close()
    conn.close()
    return redirect(url_for('student.list_students'))
