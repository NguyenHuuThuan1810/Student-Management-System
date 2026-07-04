from flask import Blueprint, render_template, session, redirect, request
from database.db import get_connection
import re

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin/dashboard")
def dashboard():

    if session.get("role") != "Admin":
        return redirect("/")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM users
        ORDER BY created_at DESC
    """)

    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin/dashboard.html",
        users=users
    )

#Add user account
@admin_bp.route("/admin/users/add", methods=["POST"])
def add_user():

    if session.get("role") != "Admin":
        return redirect("/")

    user_id = request.form["user_id"]
    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]

    if not re.fullmatch(r"U\d{3}", user_id):
        return "User ID must be in format U001, U002, U999"
    if not re.fullmatch(r"[A-Za-z0-9_]{4,30}", username):
        return "Username must be 4-30 characters and contain only letters, numbers or underscore."
    if len(password) < 6:
        return "Password must be at least 6 characters."

    if role not in ["Admin", "AcademicStaff", "Student"]:
        return "Invalid role."
    

    conn = get_connection()
    cursor = conn.cursor()

    # Kiểm tra User ID
    cursor.execute(
        "SELECT user_id FROM users WHERE user_id=%s", (user_id,))

    if cursor.fetchone():
        cursor.close()
        conn.close()
        return "User ID already exists."

    # Kiểm tra Username
    cursor.execute(
        "SELECT username FROM users WHERE username=%s", (username,))

    if cursor.fetchone():
        cursor.close()
        conn.close()
        return "Username already exists."

    sql = """
        INSERT INTO users
        (
            user_id,
            username,
            password,
            role
        )
        VALUES
        (
            %s,%s,%s,%s
        )
    """

    cursor.execute(
        sql,
        (
            user_id,
            username,
            password,
            role
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin/dashboard")

#Edit user
@admin_bp.route("/admin/users/update/<user_id>", methods=["POST"])
def update_user(user_id):

    if session.get("role") != "Admin":
        return redirect("/")

    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]


    if not re.fullmatch(r"[A-Za-z0-9_]{4,30}", username):
        return "Username must be 4-30 characters and contain only letters, numbers or underscore."
    if len(password) < 6:
        return "Password must be at least 6 characters."

    if role not in ["Admin", "AcademicStaff", "Student"]:
        return "Invalid role."

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET
            username=%s,
            password=%s,
            role=%s
        WHERE user_id=%s
    """,
    (
        username,
        password,
        role,
        user_id
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin/dashboard")

# Xóa user account
@admin_bp.route("/admin/users/delete/<user_id>")
def delete_user(user_id):

    if session.get("role") != "Admin":
        return redirect("/")
    
    #User không thể xóa chính mình
    if user_id == session.get("user_id"):
        return "You cannot delete your own account."

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE
        FROM users
        WHERE user_id=%s
    """,(user_id,))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin/dashboard")