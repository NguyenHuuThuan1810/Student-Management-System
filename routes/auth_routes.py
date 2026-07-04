from database.db import get_connection
from flask import Blueprint, render_template, request, redirect, session


auth_bp = Blueprint("auth", __name__)

# Hàm kiểm tra đăng nhập
def login(username, password):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    query = """
         SELECT user_id,
               username,
               role
        FROM users
        WHERE username=%s
        AND password=%s
    """

    cursor.execute(query, (username, password))

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user

# Hiển thị trang Login
@auth_bp.route("/")
def home():
    return render_template("login.html")


# Xử lý Login
@auth_bp.route("/login", methods=["POST"])
def login_route():

    username = request.form["username"]
    password = request.form["password"]

    user = login(username, password)

    if not user:
        return "Invalid Username or Password"

    session["user_id"] = user["user_id"]
    session["role"] = user["role"]

    if user["role"] == "Admin":
        return redirect("/admin/dashboard")

    elif user["role"] == "AcademicStaff":
        return redirect("/staff/dashboard")

    else:
        return redirect("/student/dashboard")



# Logout
@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/")
