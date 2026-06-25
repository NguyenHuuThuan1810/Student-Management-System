from flask import Blueprint, render_template, session

staff_bp = Blueprint("staff", __name__)

@staff_bp.route("/staff/dashboard")
def staff_dashboard():

    if session.get("role") != "AcademicStaff":
        return "Access Denied"

    return render_template("staff/dashboard.html")