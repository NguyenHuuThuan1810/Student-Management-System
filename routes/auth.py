from database.db import get_connection
from flask import Blueprint, render_template, request, redirect, session, flash, url_for


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
        flash("Invalid Username or Password", "danger")
        return redirect(url_for("auth.home"))

    session["user_id"] = user["user_id"]
    session["role"] = user["role"]

    if user["role"] == "Admin":
        return redirect("/admin/dashboard")

    elif user["role"] == "AcademicStaff":

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT staff_id
            FROM academic_staff
            WHERE user_id = %s
        """, (user["user_id"],))

        staff = cursor.fetchone()

        cursor.close()
        conn.close()

        if staff:
            session["staff_id"] = staff["staff_id"]

        return redirect("/staff/dashboard")

    elif user["role"] =="Student":

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT student_id
            FROM students
            WHERE user_id = %s
        """, (user["user_id"],))

        student = cursor.fetchone()

        cursor.close()
        conn.close()

        if student:
            session["student_id"] = student["student_id"]

        return redirect("/student/dashboard")
    
    else:
        flash("Vai trò tài khoản không hợp lệ.", "danger")
        return redirect(url_for("auth.home"))



# Logout
@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/")
