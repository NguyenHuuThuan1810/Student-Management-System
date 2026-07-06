from flask import Blueprint, render_template, session, flash, redirect, url_for
from database.db import get_connection
student_role_bp = Blueprint("studentrole", __name__)

@student_role_bp.route("/student/dashboard")
def dashboard():

    if session.get("role") != "Student":
        flash("Bạn không có quyền truy cập.", "danger")
        return redirect(url_for("auth.home"))

    student_id = session.get("student_id")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            s.student_id,
            s.full_name,
            s.gender,
            s.date_of_birth,
            s.address,
            s.phone,
            s.email,
            s.department,
            c.class_name,
            u.username
        FROM students s
        LEFT JOIN class_sections c
            ON s.class_id = c.class_id
        JOIN users u
            ON s.user_id = u.user_id
        WHERE s.student_id = %s
    """, (student_id,))

    student = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "student/dashboard.html",
        student=student
    )