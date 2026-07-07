from flask import Blueprint, render_template, session, redirect, request, flash, url_for
from database.db import get_connection
import re

# ==========================================
# Administrator Routes
# User Account Management
# ==========================================

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin/dashboard")
def dashboard():

    if session.get("role") != "Admin":
        flash("Bạn không có quyền truy cập.", "danger")
        return redirect(url_for("auth.home"))
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            user_id,
            username,
            role,
            created_at
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
        flash("Bạn không có quyền thực hiện chức năng này.", "danger")
        return redirect(url_for("auth.home"))

    user_id = request.form["user_id"]
    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]

    if not re.fullmatch(r"U\d{3}", user_id):
        flash("User ID phải có định dạng U001.", "danger")
        return redirect(url_for("admin.dashboard"))
    if not re.fullmatch(r"[A-Za-z0-9_]{4,30}", username):
        flash("Username chỉ gồm chữ, số hoặc dấu gạch dưới (_), từ 4 đến 30 ký tự.", "danger")
        return redirect(url_for("admin.dashboard"))
    if len(password) < 6:
        flash("Mật khẩu phải có ít nhất 6 ký tự.", "danger")
        return redirect(url_for("admin.dashboard"))

    if role not in ["Admin", "AcademicStaff", "Student"]:
        flash("Role không hợp lệ.", "danger")
        return redirect(url_for("admin.dashboard"))
    

    conn = get_connection()
    cursor = conn.cursor()

    # Kiểm tra User ID
    cursor.execute(
        "SELECT user_id FROM users WHERE user_id = %s", (user_id,))

    if cursor.fetchone():
        cursor.close()
        conn.close()
        flash("User ID đã tồn tại.", "danger")
        return redirect(url_for("admin.dashboard"))

    # Kiểm tra Username
    cursor.execute(
        "SELECT username FROM users WHERE username = %s", (username,))

    if cursor.fetchone():
        cursor.close()
        conn.close()
        flash("Username đã tồn tại.", "danger")
        return redirect(url_for("admin.dashboard"))

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
            %s, %s, %s, %s
        )
    """

    try:
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

        flash("Tạo tài khoản thành công.", "success")

    except Exception as e:

        conn.rollback()

        flash(f"Lỗi hệ thống: {str(e)}", "danger")

    finally:

        cursor.close()
        conn.close()

    return redirect(url_for("admin.dashboard"))

#Edit user
@admin_bp.route("/admin/users/update/<user_id>", methods=["POST"])
def update_user(user_id):

    if session.get("role") != "Admin":
        flash("Bạn không có quyền thực hiện chức năng này.", "danger")
        return redirect(url_for("auth.home"))

    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]


    if not re.fullmatch(r"[A-Za-z0-9_]{4,30}", username):
        flash("Username chỉ gồm chữ, số hoặc dấu gạch dưới (_), từ 4 đến 30 ký tự.", "danger")
        return redirect(url_for("admin.dashboard"))
    
    if len(password) < 6:
        flash("Mật khẩu phải có ít nhất 6 ký tự.", "danger")
        return redirect(url_for("admin.dashboard"))

    if role not in ["Admin", "AcademicStaff", "Student"]:
        flash("Role không hợp lệ.", "danger")
        return redirect(url_for("admin.dashboard"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id
        FROM users
        WHERE username = %s
        AND user_id <> %s
    """, (username, user_id))

    if cursor.fetchone():
        cursor.close()
        conn.close()
        flash("Username đã tồn tại.", "danger")
        return redirect(url_for("admin.dashboard"))
    
    if user_id == session.get("user_id") and role != "Admin":
        flash("Bạn không thể thay đổi vai trò của chính mình.", "warning")
        return redirect(url_for("admin.dashboard"))
    
    
    try:

        cursor.execute("""
            UPDATE users
            SET
                username = %s,
                password = %s,
                role = %s
            WHERE user_id = %s
        """,
        (
            username,
            password,
            role,
            user_id
        ))

        conn.commit()

        flash("Cập nhật tài khoản thành công.", "success")

    except Exception as e:

        conn.rollback()

        flash(f"Lỗi hệ thống: {str(e)}", "danger")

    finally:

        cursor.close()
        conn.close()

    return redirect(url_for("admin.dashboard"))

# Xóa user account
@admin_bp.route("/admin/users/delete/<user_id>", methods=["POST"])
def delete_user(user_id):

    if session.get("role") != "Admin":
        flash("Bạn không có quyền thực hiện chức năng này.", "danger")
        return redirect(url_for("auth.home"))
    
    #User không thể xóa chính mình
    if user_id == session.get("user_id"):
        flash("Bạn không thể xóa chính tài khoản của mình.", "warning")
        return redirect(url_for("admin.dashboard"))

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            DELETE
            FROM users
            WHERE user_id = %s
        """, (user_id,))

        if cursor.rowcount == 0:
            flash("Không tìm thấy tài khoản.", "warning")
            return redirect(url_for("admin.dashboard"))
        
        conn.commit()

        flash("Xóa tài khoản thành công.", "success")

    except Exception as e:

        conn.rollback()

        flash(f"Lỗi hệ thống: {str(e)}", "danger")

    finally:

        cursor.close()
        conn.close()

    return redirect(url_for("admin.dashboard"))