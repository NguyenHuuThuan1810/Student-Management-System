from flask import Flask

from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.staff_routes import staff_bp
from routes.student_routes import student_bp

app = Flask(__name__)

app.secret_key = "student_management_secret_key"

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(student_bp)

if __name__ == "__main__":
    app.run(debug=True)