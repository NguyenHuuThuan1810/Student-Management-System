from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db import get_connection

grade_bp = Blueprint('grade', __name__)

@grade_bp.route('/grades')
def view_grades():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT g.grade_id, s.student_name, c.course_name, g.assignment_score, g.exam_score, g.final_score
        FROM Grade g
        JOIN Student s ON g.student_id = s.student_id
        JOIN Course c ON g.course_id = c.course_id
    """
    cursor.execute(query)
    grades = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('staff/dashboard.html', grades=grades)

@grade_bp.route('/grade/save', methods=['POST'])
def save_grade():
    student_id = request.form.get('student_id')
    course_id = request.form.get('course_id')
    assignment_score = float(request.form.get('assignment_score', 0))
    exam_score = float(request.form.get('exam_score', 0))
    
    #tính điểm tổng kết hệ 10 
    final_score = (assignment_score * 0.4) + (exam_score * 0.6)
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Kiểm tra xem sinh viên đã có bản ghi điểm môn này chưa
        cursor.execute("SELECT grade_id FROM Grade WHERE student_id = %s AND course_id = %s", (student_id, course_id))
        existing_grade = cursor.fetchone()
        
        if existing_grade:
            # Update Grade
            query = """
                UPDATE Grade 
                SET assignment_score = %s, exam_score = %s, final_score = %s 
                WHERE student_id = %s AND course_id = %s
            """
            cursor.execute(query, (assignment_score, exam_score, final_score, student_id, course_id))
        else:
            # Add Grade
            query = """
                INSERT INTO Grade (student_id, course_id, assignment_score, exam_score, final_score) 
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (student_id, course_id, assignment_score, exam_score, final_score))
            
        conn.commit()
        flash("Cập nhật điểm và tính toán điểm tổng kết thành công!", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Lỗi hệ thống: {str(e)}", "danger")
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('grade.view_grades'))

#Tính toán quy đổi sang điểm GPA hệ 4 từ điểm hệ 10
def calculate_gpa_4(final_score):
    if final_score >= 8.5: return 4.0
    elif final_score >= 7.0: return 3.0
    elif final_score >= 5.5: return 2.0
    elif final_score >= 4.0: return 1.0
    else: return 0.0