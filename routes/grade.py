from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.db import get_connection


# ==========================================
# Grade Management Routes
# Handles Grade CRUD and Grade Calculation
# ==========================================

grade_bp = Blueprint('grade', __name__)

# Hàm tính điểm tổng kết hệ 10 và quy đổi điểm chữ
def process_grading(attendance, midterm, final):
    total = (attendance * 0.1) + (midterm * 0.3) + (final * 0.6)
    if total >= 8.5: letter = 'A'
    elif total >= 8.0: letter = 'B+'
    elif total >= 7.0: letter = 'B'
    elif total >= 6.5: letter = 'C+'
    elif total >= 5.5: letter = 'C'
    elif total >= 5.0: letter = 'D+'
    elif total >= 4.0: letter = 'D'
    else: letter = 'F'
    return round(total, 2), letter

# Display grade list
@grade_bp.route('/grades')
def view_grades():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Đồng bộ chính xác tên bảng và cột theo schema mới
    query = """
        SELECT g.grade_id, s.full_name AS student_name, c.course_name, 
               g.attendance_score, g.midterm_score, g.final_score, g.total_score, g.letter_grade
        FROM grades g
        JOIN students s ON g.student_id = s.student_id
        JOIN courses c ON g.course_id = c.course_id
    """
    cursor.execute(query)
    grades = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('staff/dashboard.html', grades=grades)

# Save or update grade
@grade_bp.route('/grade/save', methods=['POST'])
def save_grade():
    student_id = request.form.get('student_id')
    course_id = request.form.get('course_id')
    try:
        attendance_score = float(request.form.get('attendance_score', 0))
        midterm_score = float(request.form.get('midterm_score', 0))
        final_score = float(request.form.get('final_score', 0))
    except ValueError:
        flash("Điểm nhập không hợp lệ.","danger")
        return redirect(url_for('grade.view_grades'))
    
    # Lấy staff_id của người đang đăng nhập từ session để làm khóa ngoại, tránh lỗi CONSTRAINT fk_grade_staff
    staff_id = session.get('staff_id') 
    
    if not staff_id:
        flash("Phiên đăng nhập đã hết hạn.", "danger")
        return redirect(url_for("auth.home"))
    
    # Xác thực điểm số
    for score in [attendance_score, midterm_score, final_score]:
        if score < 0 or score > 10:
            flash("Điểm phải nằm trong khoảng từ 0 đến 10.", "danger")
            return redirect(url_for('grade.view_grades'))
    
    # Tính điểm tổng kết & xếp loại điểm chữ
    total_score, letter_grade = process_grading(attendance_score, midterm_score, final_score)
    
    conn = get_connection()
    cursor = conn.cursor()

    # Kiểm tra sinh viên đã đăng ký môn học chưa
    cursor.execute("""
        SELECT enrollment_id
        FROM enrollments
        WHERE student_id = %s
        AND course_id = %s
        AND status IN ('Registered', 'Completed')
    """, (student_id, course_id))

    enrollment = cursor.fetchone()

    if not enrollment:
        flash("Sinh viên chưa đăng ký môn học này.", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for('grade.view_grades'))

    try:
        # Kiểm tra xem đã có bản ghi điểm chưa
        cursor.execute("SELECT grade_id FROM grades WHERE student_id = %s AND course_id = %s", (student_id, course_id))
        existing_grade = cursor.fetchone()
        
        if existing_grade:
            # Cập nhật điểm (Tên bảng và cột viết thường theo DB mới)
            query = """
                UPDATE grades 
                SET attendance_score = %s, midterm_score = %s, final_score = %s, total_score = %s, letter_grade = %s, staff_id = %s
                WHERE student_id = %s AND course_id = %s
            """
            cursor.execute(query, (attendance_score, midterm_score, final_score, total_score, letter_grade, staff_id, student_id, course_id))
        else:
            # Tạo grade_ID tiếp theo
            cursor.execute("""
                SELECT grade_id
                FROM grades
                ORDER BY CAST(SUBSTRING(grade_id,2) AS UNSIGNED) DESC
                LIMIT 1
            """)

            last_grade = cursor.fetchone()

            if last_grade:
                next_number = int(last_grade["grade_id"][1:]) + 1
            else:
                next_number = 1

            new_grade_id = f"G{next_number:03d}"

            query = """
                INSERT INTO grades (grade_id, student_id, staff_id, course_id, attendance_score, midterm_score, final_score, total_score, letter_grade) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (new_grade_id, student_id, staff_id, course_id, attendance_score, midterm_score, final_score, total_score, letter_grade))
            
        conn.commit()
        flash("Cập nhật điểm và tính toán điểm tổng kết thành công!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Lỗi hệ thống: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('grade.view_grades'))