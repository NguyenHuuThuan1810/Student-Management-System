from flask import Blueprint, render_template, session, flash, redirect, url_for

student_bp = Blueprint("student", __name__)

@student_bp.route("/student/dashboard")
def student_dashboard():

    if session.get("role") != "Student":
        flash("Bạn không có quyền truy cập.", "danger")
        return redirect(url_for("auth.home"))

    if not session.get("student_id"):
        flash("Phiên đăng nhập đã hết hạn.", "danger")
        return redirect(url_for("auth.home"))

    return render_template("student/dashboard.html")