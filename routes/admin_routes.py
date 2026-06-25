from flask import Blueprint, render_template, session

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin/dashboard")
def admin_dashboard():

    if session.get("role") != "Admin":
        return "Access Denied"

    return render_template("admin/dashboard.html")