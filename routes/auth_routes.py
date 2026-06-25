from database.db import get_connection
from flask import Blueprint, render_template, request, redirect, session


auth_bp = Blueprint("auth", __name__)

# Hàm kiểm tra đăng nhập
def login(username, password):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT user_id, role
        FROM users
        WHERE username=%s
        AND password=%s
    """

    cursor.execute(query, (username, password))

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result

# Hiển thị trang Login
@auth_bp.route("/")
def home():
    return render_template("login.html")


# Xử lý Login
@auth_bp.route("/login", methods=["POST"])
def login_route():

    username = request.form["username"]
    password = request.form["password"]

    result = login(username, password)

    if result:

        role = result["role"]

        session["role"] = role

        if role == "Admin":
            return redirect("/admin/dashboard")

        elif role == "AcademicStaff":
            return redirect("/staff/dashboard")

        elif role == "Student":
            return redirect("/student/dashboard")

    return "Invalid Username or Password"


# Logout
@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/")
