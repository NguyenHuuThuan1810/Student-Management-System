from flask import Blueprint, render_template, session

student_bp = Blueprint("student", __name__)

@student_bp.route("/student/dashboard")
def student_dashboard():

    if session.get("role") != "Student":
        return "Access Denied"

    return render_template("student/dashboard.html")