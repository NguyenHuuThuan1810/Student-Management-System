CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(100),
    role ENUM('Admin','AcademicStaff','Student')
);
INSERT INTO users(username,password,role)
VALUES
('admin','123','Admin'),
('staff01','123','AcademicStaff'),
('student01','123','Student');