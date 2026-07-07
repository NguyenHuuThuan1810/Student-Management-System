import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        #host="localhost",
        host="db",
        user="root",
        password="123456",
        database="student_management"
    )

    return connection