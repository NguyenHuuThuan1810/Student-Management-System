from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_connection 
import uuid
from datetime import datetime

enrollment_bp = Blueprint('enrollment', __name__)

@enrollment_bp.route('/enrollments')
def view_enrollments():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Sửa Student -> students, Enrollment -> enrollments, s.student_name -> s.full_name
    query = """
        SELECT e.enrollment_id, s.full_name AS student_name, c.course_name, e.semester, e.status, e.enrollment_date 
        FROM enrollments e
        JOIN students s ON e.student_id = s.student_id
        JOIN courses c ON e.course_id = c.course_id
    """
    cursor.execute(query)
    enrollments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('student/dashboard.html', enrollments=enrollments)

@enrollment_bp.route('/enroll/add', methods=['POST'])
def register_course():
    student_id = request.form.get('student_id')
    course_id = request.form.get('course_id')
    semester = request.form.get('semester', '2025-2026 HK2') # Mặc định học kỳ theo định dạng dữ liệu mẫu
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Sinh chuỗi ngẫu nhiên cho enrollment_id (VARCHAR(20)) thay vì để trống tự tăng
        new_enroll_id = "EN" + str(uuid.uuid4().hex[:10]).upper()
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
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "DELETE FROM enrollments WHERE enrollment_id = %s"
        cursor.execute(query, (enrollment_id,))
        conn.commit()
        flash("Đã hủy đăng ký học phần thành công!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Không thể hủy đăng ký: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('enrollment.view_enrollments'))