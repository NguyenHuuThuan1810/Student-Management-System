from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_connection

student_bp = Blueprint('student', __name__)


@student_bp.route('/students')
def list_students():
    q = request.args.get('q', '').strip()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    if q:
        cursor.execute("""
            SELECT * FROM students
            WHERE student_id LIKE %s OR full_name LIKE %s
               OR email LIKE %s OR department LIKE %s
            ORDER BY student_id
        """, (f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%'))
    else:
        cursor.execute("SELECT * FROM students ORDER BY student_id")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('students/list.html', students=students, q=q)


@student_bp.route('/students/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        student_id = request.form.get('student_id', '').strip()
        full_name  = request.form.get('full_name', '').strip()
        gender     = request.form.get('gender', '').strip()
        dob        = request.form.get('date_of_birth', '').strip()
        address    = request.form.get('address', '').strip()
        phone      = request.form.get('phone', '').strip()
        email      = request.form.get('email', '').strip() or None
        department = request.form.get('department', '').strip()

        if not student_id or not full_name or not gender or not dob:
            flash('Vui lòng điền đầy đủ các trường bắt buộc (*).', 'danger')
            return render_template('students/add.html')

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO students
                    (student_id, full_name, gender, date_of_birth, address, phone, email, department)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (student_id, full_name, gender, dob, address, phone, email, department))
            conn.commit()
            flash(f'Thêm sinh viên {full_name} thành công!', 'success')
            return redirect(url_for('student.list_students'))
        except Exception as e:
            conn.rollback()
            flash(f'Lỗi: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('students/add.html')


@student_bp.route('/students/<student_id>')
def view_student(student_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()
    if not student:
        flash('Không tìm thấy sinh viên.', 'danger')
        return redirect(url_for('student.list_students'))
    return render_template('students/view.html', student=student)


@student_bp.route('/students/<student_id>/edit', methods=['GET', 'POST'])
def edit_student(student_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()

    if not student:
        flash('Không tìm thấy sinh viên.', 'danger')
        return redirect(url_for('student.list_students'))

    if request.method == 'POST':
        full_name  = request.form.get('full_name', '').strip()
        gender     = request.form.get('gender', '').strip()
        dob        = request.form.get('date_of_birth', '').strip()
        address    = request.form.get('address', '').strip()
        phone      = request.form.get('phone', '').strip()
        email      = request.form.get('email', '').strip() or None
        department = request.form.get('department', '').strip()

        if not full_name or not gender or not dob:
            flash('Vui lòng điền đầy đủ các trường bắt buộc (*).', 'danger')
            return render_template('students/edit.html', student=student)

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE students
                SET full_name=%s, gender=%s, date_of_birth=%s,
                    address=%s, phone=%s, email=%s, department=%s
                WHERE student_id=%s
            """, (full_name, gender, dob, address, phone, email, department, student_id))
            conn.commit()
            flash(f'Cập nhật sinh viên {full_name} thành công!', 'success')
            return redirect(url_for('student.view_student', student_id=student_id))
        except Exception as e:
            conn.rollback()
            flash(f'Lỗi: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('students/edit.html', student=student)


@student_bp.route('/students/<student_id>/delete', methods=['POST'])
def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT full_name FROM students WHERE student_id = %s", (student_id,))
    student = cursor.fetchone()
    if student:
        cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
        conn.commit()
        flash(f'Đã xoá sinh viên {student["full_name"]}.', 'warning')
    else:
        flash('Không tìm thấy sinh viên.', 'danger')
    cursor.close()
    conn.close()
    return redirect(url_for('student.list_students'))
