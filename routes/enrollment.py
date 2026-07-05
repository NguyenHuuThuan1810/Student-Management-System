from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db import get_connection 
from datetime import datetime

enrollment_bp = Blueprint('enrollment', __name__)

@enrollment_bp.route('/enrollments')
def view_enrollments():
    if session.get("role") != "Student":
        flash("Bạn không có quyền thực hiện chức năng này.", "danger")
        return redirect(url_for("auth.home"))

    student_id = session.get("student_id")

    if not student_id:
        flash("Phiên đăng nhập đã hết hạn.", "danger")
        return redirect(url_for("auth.home"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            e.enrollment_id,
            c.course_name,
            e.semester,
            e.status,
            e.enrollment_date
        FROM enrollments e
        JOIN courses c
            ON e.course_id = c.course_id
        WHERE e.student_id = %s
        ORDER BY e.enrollment_date DESC
    """

    cursor.execute(query, (student_id,))
    enrollments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "student/dashboard.html",
        enrollments=enrollments
    )

@enrollment_bp.route('/enroll/add', methods=['POST'])
def register_course():
    if session.get("role") != "Student":
        flash("Bạn không có quyền thực hiện chức năng này.", "danger")
        return redirect(url_for("auth.home"))
    
    student_id = session.get('student_id')

    if not student_id:
        flash("Phiên đăng nhập đã hết hạn.", "danger")
        return redirect(url_for("auth.home"))

    course_id = request.form.get('course_id')
    semester = request.form.get('semester', '2025-2026 HK2') # Mặc định học kỳ theo định dạng dữ liệu mẫu
    
    conn = get_connection()
    cursor = conn.cursor()

    # Kiểm tra sinh viên đã đăng ký môn học này trong học kỳ chưa
    cursor.execute("""
        SELECT enrollment_id
        FROM enrollments
        WHERE student_id = %s
        AND course_id = %s
        AND semester = %s
    """, (student_id, course_id, semester))

    existing_enrollment = cursor.fetchone()

    if existing_enrollment:
        flash("Bạn đã đăng ký môn học này trong học kỳ này.", "warning")
        cursor.close()
        conn.close()
        return redirect(url_for("enrollment.view_enrollments"))
    try:
        # Generate next enrollment ID
        cursor.execute("""
            SELECT enrollment_id
            FROM enrollments
            ORDER BY CAST(SUBSTRING(enrollment_id, 3) AS UNSIGNED) DESC
            LIMIT 1
        """)

        last_enrollment = cursor.fetchone()

        if last_enrollment:
            next_number = int(last_enrollment[0][2:]) + 1
        else:
            next_number = 1

        new_enroll_id = f"EN{next_number:03d}"

        current_date = datetime.now().strftime('%Y-%m-%d')
        
        query = """
            INSERT INTO enrollments (enrollment_id, student_id, course_id, semester, status, enrollment_date) 
            VALUES (%s, %s, %s, %s, 'Registered', %s)
        """
        cursor.execute(query, (new_enroll_id, student_id, course_id, semester, current_date))
        conn.commit()
        flash("Đăng ký học phần thành công!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Lỗi khi đăng ký: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('enrollment.view_enrollments'))

# Đổi kiểu nhận dữ liệu <int:enrollment_id> thành chuỗi string thông thường vì DB định dạng VARCHAR
@enrollment_bp.route('/enroll/cancel/<string:enrollment_id>', methods=['POST'])
def cancel_enrollment(enrollment_id):

    if session.get("role") != "Student":
            flash("Bạn không có quyền thực hiện chức năng này.", "danger")
            return redirect(url_for("auth.home"))
    
    student_id = session.get("student_id")

    if not student_id:
        flash("Phiên đăng nhập đã hết hạn.", "danger")
        return redirect(url_for("auth.home"))

    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            DELETE FROM enrollments
            WHERE enrollment_id = %s
            AND student_id = %s
        """
        cursor.execute(query, (enrollment_id, student_id))
        conn.commit()
        flash("Đã hủy đăng ký học phần thành công!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Không thể hủy đăng ký: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('enrollment.view_enrollments'))