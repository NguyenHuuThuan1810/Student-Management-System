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

# Display grade list (Dành cho cả Staff quản lý và Student xem điểm của mình)
@grade_bp.route('/grades')
def view_grades():
    user_role = session.get("role")
    
    # Chặn nếu người dùng chưa đăng nhập hoặc không đúng quyền
    if user_role not in ["AcademicStaff", "Student"]:
        flash("Bạn không có quyền thực hiện chức năng này.", "danger")
        return redirect(url_for("auth.home"))
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    if user_role == "AcademicStaff":
        # 1. Logic dành cho STAFF: Xem TẤT CẢ các điểm số của mọi sinh viên
        query = """
            SELECT
                    g.grade_id,
                    g.student_id,
                    g.course_id,
                    s.full_name AS student_name,
                    c.course_name,
                    g.attendance_score,
                    g.midterm_score,
                    g.final_score,
                    g.total_score,
                    g.letter_grade
                FROM grades g
                JOIN students s
                ON g.student_id=s.student_id
                JOIN courses c
                ON g.course_id=c.course_id
                ORDER BY s.full_name
        """
        cursor.execute(query)
        grades = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('staff/grades.html', grades=grades)
        
    elif user_role == "Student":
        # 2. Logic dành cho STUDENT: Chỉ lọc ra điểm của đúng mã sinh viên đang đăng nhập
        student_id = session.get("student_id")
        if not student_id:
            flash("Không tìm thấy thông tin phiên đăng nhập sinh viên.", "danger")
            return redirect(url_for("auth.home"))
            
        query = """
            SELECT g.grade_id, c.course_name, 
                   g.attendance_score, g.midterm_score, g.final_score, g.total_score, g.letter_grade
            FROM grades g
            JOIN courses c ON g.course_id = c.course_id
            WHERE g.student_id = %s
        """
        cursor.execute(query, (student_id,))
        student_grades = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Trả về giao diện bảng điểm riêng của sinh viên
        return render_template('student/grades.html', grades=student_grades)

# Save or update grade
@grade_bp.route('/grade/save', methods=['POST'])
def save_grade():
    if session.get("role") != "AcademicStaff":
        flash("Bạn không có quyền thực hiện chức năng này.", "danger")
        return redirect(url_for("auth.home"))
    
    student_id = request.form.get('student_id')
    course_id = request.form.get('course_id')
    if not student_id or not course_id:
        flash("Thiếu thông tin sinh viên hoặc môn học.", "danger")
        return redirect(url_for("grade.view_grades"))
    
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
    cursor = conn.cursor(dictionary=True)

    # Kiểm tra Student tồn tại
    cursor.execute("""
        SELECT student_id
        FROM students
        WHERE student_id = %s
    """, (student_id,))

    if not cursor.fetchone():
        flash("Sinh viên không tồn tại.", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for("grade.view_grades"))

    # Kiểm tra Course tồn tại
    cursor.execute("""
        SELECT course_id
        FROM courses
        WHERE course_id = %s
    """, (course_id,))

    if not cursor.fetchone():
        flash("Môn học không tồn tại.", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for("grade.view_grades"))

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