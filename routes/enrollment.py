from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_connection 


enrollment_bp = Blueprint('enrollment', __name__)


@enrollment_bp.route('/enrollments')
def view_enrollments():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Query hiển thị danh sách
    query = """
        SELECT e.enrollment_id, s.student_name, c.course_name, e.enrollment_date 
        FROM Enrollment e
        JOIN Student s ON e.student_id = s.student_id
        JOIN Course c ON e.course_id = c.course_id
    """
    cursor.execute(query)
    enrollments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Render ra đúng file dashboard hoặc giao diện tương ứng (Ví dụ dưới đây tùy thuộc vào UI bạn thống nhất)
    return render_template('student/dashboard.html', enrollments=enrollments)


@enrollment_bp.route('/enroll/add', methods=['POST'])
def register_course():
    student_id = request.form.get('student_id')
    course_id = request.form.get('course_id')
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "INSERT INTO Enrollment (student_id, course_id, enrollment_date) VALUES (%s, %s, NOW())"
        cursor.execute(query, (student_id, course_id))
        conn.commit()
        flash("Đăng ký học phần thành công!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Lỗi khi đăng ký: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('enrollment.view_enrollments'))

# Cancel Enrollment
@enrollment_bp.route('/enroll/cancel/<int:enrollment_id>', methods=['POST'])
def cancel_enrollment(enrollment_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = "DELETE FROM Enrollment WHERE enrollment_id = %s"
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