from flask import Blueprint, render_template, session, flash, redirect, url_for
from database.db import get_connection
staff_bp = Blueprint("staff", __name__, url_prefix="/staff")

@staff_bp.route("/dashboard")
def staff_dashboard():
    if session.get("role") != "AcademicStaff":
        flash("Bạn không có quyền truy cập.", "danger")
        return redirect(url_for("auth.home"))

    if not session.get("staff_id"):
        flash("Phiên đăng nhập đã hết hạn.", "danger")
        return redirect(url_for("auth.home"))
    


    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Total Students
    cursor.execute("SELECT COUNT(*) total FROM students")
    total_students = cursor.fetchone()["total"]

    # Total Courses
    cursor.execute("SELECT COUNT(*) total FROM courses")
    total_courses = cursor.fetchone()["total"]

    # Total Grades
    cursor.execute("SELECT COUNT(*) total FROM grades")
    total_grades = cursor.fetchone()["total"]

    # Average Score
    cursor.execute("SELECT ROUND(AVG(total_score),2) avg_score FROM grades")
    average_score = cursor.fetchone()["avg_score"]

    # Recent Students
    cursor.execute("""
    SELECT student_id, full_name
    FROM students
    ORDER BY student_id DESC
    LIMIT 5
    """)

    recent_students = cursor.fetchall()

    # Recent Courses
    cursor.execute("""
    SELECT course_id, course_name
    FROM courses
    ORDER BY course_id DESC
    LIMIT 5
    """)

    recent_courses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "staff/dashboard.html",
        total_students=total_students,
        total_courses=total_courses,
        total_grades=total_grades,
        average_score=average_score,
        recent_students=recent_students,
        recent_courses=recent_courses
    )

@staff_bp.route("/student")
def staff_student():
    if session.get("role") != "AcademicStaff":
        flash("Bạn không có quyền truy cập.", "danger")
        return redirect(url_for("auth.home"))

    if not session.get("staff_id"):
        flash("Phiên đăng nhập đã hết hạn.", "danger")
        return redirect(url_for("auth.home"))
    return render_template("staff/student.html")

@staff_bp.route("/course")
def staff_course():
    if session.get("role") != "AcademicStaff":
        flash("Bạn không có quyền truy cập.", "danger")
        return redirect(url_for("auth.home"))

    if not session.get("staff_id"):
        flash("Phiên đăng nhập đã hết hạn.", "danger")
        return redirect(url_for("auth.home"))
    return render_template("staff/course.html")

@staff_bp.route("/enrollment")
def staff_enrollment():
    if session.get("role") != "AcademicStaff":
        flash("Bạn không có quyền truy cập.", "danger")
        return redirect(url_for("auth.home"))

    if not session.get("staff_id"):
        flash("Phiên đăng nhập đã hết hạn.", "danger")
        return redirect(url_for("auth.home"))
    return render_template("staff/enrollment.html")

@staff_bp.route("/grade")
def staff_grade():
    if session.get("role") != "AcademicStaff":
        flash("Bạn không có quyền truy cập.", "danger")
        return redirect(url_for("auth.home"))

    if not session.get("staff_id"):
        flash("Phiên đăng nhập đã hết hạn.", "danger")
        return redirect(url_for("auth.home"))
    return render_template("staff/grade.html")
