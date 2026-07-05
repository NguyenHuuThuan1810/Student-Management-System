from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import re
from database.db import get_connection

# ==================================================
# Course Management Routes
# Handles CRUD operations for Course
# ==================================================

course_bp = Blueprint('course', __name__)

# Display all courses and search
@course_bp.route('/courses')
def list_courses():

    if session.get("role") != "AcademicStaff":
        flash("Bạn không có quyền thực hiện chức năng này.", "danger")
        return redirect(url_for("auth.home"))

    q = request.args.get('q', '').strip()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    if q:
        cursor.execute("""
            SELECT course_id, course_name, credits, description 
            FROM courses
            WHERE course_id LIKE %s OR course_name LIKE %s
            ORDER BY course_id
        """, (f'%{q}%', f'%{q}%'))
    else:
        cursor.execute("SELECT course_id, course_name, credits, description FROM courses ORDER BY course_id")
    courses = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('courses/list.html', courses=courses, q=q)

# Add a new course
@course_bp.route('/courses/add', methods=['GET', 'POST'])
def add_course():

    if session.get("role") != "AcademicStaff":
        flash("Bạn không có quyền thực hiện chức năng này.", "danger")
        return redirect(url_for("auth.home"))
    
    if request.method == 'POST':
        course_id   = request.form.get('course_id', '').strip()
        course_name = request.form.get('course_name', '').strip()
        credits_str = request.form.get('credits', '').strip()
        description = request.form.get('description', '').strip()

        if not course_id or not course_name or not credits_str:
            flash('Vui lòng điền đầy đủ các trường bắt buộc (*).', 'danger')
            return render_template('courses/add.html')
        if not re.fullmatch(r"C\d{3}", course_id):
            flash("Course ID phải có định dạng C001.", "danger")
            return render_template("courses/add.html")
        if len(course_name) > 100:
            flash("Tên môn học quá dài.", "danger")
            return render_template("courses/add.html")

        try:
            credits = int(credits_str)
            if credits < 1 or credits > 10:
                raise ValueError
        except ValueError:
            flash('Số tín chỉ phải nằm trong khoảng từ 1 đến 10.', 'danger')
            return render_template('courses/add.html')
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT course_id
            FROM courses
            WHERE course_name=%s
            AND course_id<>%s
        """, (course_name, course_id))

        if cursor.fetchone():
            cursor.close()
            conn.close()
            flash("Tên môn học đã tồn tại.", "danger")
            return render_template("courses/add.html")


        # Kiểm tra Course ID đã tồn tại
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT course_id FROM courses WHERE course_id=%s",
            (course_id,)
        )

        if cursor.fetchone():
            cursor.close()
            conn.close()
            flash("Course ID đã tồn tại.", "danger")
            return render_template("courses/add.html")

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO courses (course_id, course_name, credits, description)
                VALUES (%s, %s, %s, %s)
            """, (course_id, course_name, credits, description))
            conn.commit()
            flash(f'Thêm môn học "{course_name}" thành công!', 'success')
            return redirect(url_for('course.list_courses'))
        except Exception as e:
            conn.rollback()
            flash(f"Lỗi hệ thống: {str(e)}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template('courses/add.html')

# View course details
@course_bp.route('/courses/<course_id>')
def view_course(course_id):

    if session.get("role") != "AcademicStaff":
        flash("Bạn không có quyền thực hiện chức năng này.", "danger")
        return redirect(url_for("auth.home"))
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT course_id, course_name, credits, description FROM courses WHERE course_id = %s", (course_id,))
    course = cursor.fetchone()
    cursor.close()
    conn.close()
    if not course:
        flash('Không tìm thấy môn học.', 'danger')
        return redirect(url_for('course.list_courses'))
    return render_template('courses/view.html', course=course)

# Update course information
@course_bp.route('/courses/<course_id>/edit', methods=['GET', 'POST'])
def edit_course(course_id):

    if session.get("role") != "AcademicStaff":
        flash("Bạn không có quyền thực hiện chức năng này.", "danger")
        return redirect(url_for("auth.home"))
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT course_id, course_name, credits, description FROM courses WHERE course_id = %s", (course_id,))
    course = cursor.fetchone()
    cursor.close()
    conn.close()

    if not course:
        flash('Không tìm thấy môn học.', 'danger')
        return redirect(url_for('course.list_courses'))

    if request.method == 'POST':
        course_name = request.form.get('course_name', '').strip()
        credits_str = request.form.get('credits', '').strip()
        description = request.form.get('description', '').strip()

        if not course_name or not credits_str:
            flash('Vui lòng điền đầy đủ các trường bắt buộc (*).', 'danger')
            return render_template('courses/edit.html', course=course)
        if len(course_name) > 100:
            flash("Tên môn học quá dài.", "danger")
            return render_template(
                "courses/edit.html",
                course=course
            )
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT course_id
            FROM courses
            WHERE course_name=%s
            AND course_id<>%s
        """, (course_name, course_id))

        if cursor.fetchone():
            cursor.close()
            conn.close()
            flash("Tên môn học đã tồn tại.", "danger")
            return render_template(
                "courses/edit.html",
                course=course
            )

        try:
            credits = int(credits_str)
            if credits < 1 or credits > 10:
                raise ValueError
        except ValueError:
            flash('Số tín chỉ phải nằm trong khoảng từ 1 đến 10.', 'danger')
            return render_template('courses/edit.html', course=course)


        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE courses
                SET course_name=%s, credits=%s, description=%s
                WHERE course_id=%s
            """, (course_name, credits, description, course_id))
            conn.commit()
            flash(f'Cập nhật môn học "{course_name}" thành công!', 'success')
            return redirect(url_for('course.view_course', course_id=course_id))
        except Exception as e:
            conn.rollback()
            flash(f"Lỗi hệ thống: {str(e)}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template('courses/edit.html', course=course)

# Delete a course
@course_bp.route('/courses/<course_id>/delete', methods=['POST'])
def delete_course(course_id):

    if session.get("role") != "AcademicStaff":
        flash("Bạn không có quyền thực hiện chức năng này.", "danger")
        return redirect(url_for("auth.home"))
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT course_name FROM courses WHERE course_id = %s", (course_id,))
    course = cursor.fetchone()
    if course:
        try:
            cursor.execute("DELETE FROM courses WHERE course_id = %s", (course_id,))
            conn.commit()
            flash(f'Đã xoá môn học "{course["course_name"]}".', 'warning')

        except Exception as e:
            conn.rollback()
            flash("Không thể xoá môn học vì đang được sử dụng.", "danger")
    else:
        flash('Không tìm thấy môn học.', 'danger')
    cursor.close()
    conn.close()
    return redirect(url_for('course.list_courses'))
