from flask import Blueprint, render_template, session, flash, redirect, url_for

staff_bp = Blueprint("staff", __name__)

@staff_bp.route("/staff/dashboard")
def staff_dashboard():

    if session.get("role") != "AcademicStaff":
        flash("Bạn không có quyền truy cập.", "danger")
        return redirect(url_for("auth.home"))

    if not session.get("staff_id"):
        flash("Phiên đăng nhập đã hết hạn.", "danger")
        return redirect(url_for("auth.home"))

    return render_template("staff/dashboard.html")