-- Student Management System - Full MySQL schema and sample data
-- Database Developer deliverable

CREATE DATABASE IF NOT EXISTS student_management
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE student_management;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS reports;
DROP TABLE IF EXISTS grades;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS class_sections;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS academic_staff;
DROP TABLE IF EXISTS administrators;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. USERS
CREATE TABLE users (
    user_id VARCHAR(20) PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'AcademicStaff', 'Student') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. ADMINISTRATORS
CREATE TABLE administrators (
    admin_id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    CONSTRAINT fk_admin_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. ACADEMIC STAFF
CREATE TABLE academic_staff (
    staff_id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    department VARCHAR(100),
    CONSTRAINT fk_staff_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. COURSES
CREATE TABLE courses (
    course_id VARCHAR(20) PRIMARY KEY,
    course_name VARCHAR(150) NOT NULL,
    credits INT NOT NULL,
    description TEXT,
    CONSTRAINT chk_course_credits
        CHECK (credits > 0 AND credits <= 10)
) ENGINE=InnoDB;

-- 5. CLASS SECTIONS
CREATE TABLE class_sections (
    class_id VARCHAR(20) PRIMARY KEY,
    staff_id VARCHAR(20) NOT NULL,
    class_name VARCHAR(100) NOT NULL,
    CONSTRAINT fk_class_staff
        FOREIGN KEY (staff_id) REFERENCES academic_staff(staff_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 6. STUDENTS
CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY,
    class_id VARCHAR(20),
    user_id VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    date_of_birth DATE,
    address VARCHAR(255),
    phone VARCHAR(15),
    email VARCHAR(100) UNIQUE,
    department VARCHAR(100),
    CONSTRAINT fk_student_class
        FOREIGN KEY (class_id) REFERENCES class_sections(class_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT fk_student_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- 7. ENROLLMENTS / COURSE REGISTRATION
CREATE TABLE enrollments (
    enrollment_id VARCHAR(20) PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    course_id VARCHAR(20) NOT NULL,
    semester VARCHAR(20) NOT NULL,
    status ENUM('Registered', 'Completed', 'Dropped') NOT NULL DEFAULT 'Registered',
    enrollment_date DATE NOT NULL,
    CONSTRAINT fk_enrollment_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_enrollment_course
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT uq_enrollment_student_course_semester
        UNIQUE (student_id, course_id, semester)
) ENGINE=InnoDB;

-- 8. GRADES
CREATE TABLE grades (
    grade_id VARCHAR(20) PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    staff_id VARCHAR(20) NOT NULL,
    course_id VARCHAR(20) NOT NULL,
    attendance_score DECIMAL(4,2) DEFAULT 0,
    midterm_score DECIMAL(4,2) DEFAULT 0,
    final_score DECIMAL(4,2) DEFAULT 0,
    total_score DECIMAL(4,2) DEFAULT 0,
    letter_grade VARCHAR(2),
    CONSTRAINT fk_grade_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_grade_staff
        FOREIGN KEY (staff_id) REFERENCES academic_staff(staff_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_grade_course
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT uq_grade_student_course
        UNIQUE (student_id, course_id),
    CONSTRAINT chk_grade_attendance
        CHECK (attendance_score >= 0 AND attendance_score <= 10),
    CONSTRAINT chk_grade_midterm
        CHECK (midterm_score >= 0 AND midterm_score <= 10),
    CONSTRAINT chk_grade_final
        CHECK (final_score >= 0 AND final_score <= 10),
    CONSTRAINT chk_grade_total
        CHECK (total_score >= 0 AND total_score <= 10)
) ENGINE=InnoDB;

-- 9. REPORTS
CREATE TABLE reports (
    report_id VARCHAR(20) PRIMARY KEY,
    staff_id VARCHAR(20) NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    generated_date DATE NOT NULL,
    CONSTRAINT fk_report_staff
        FOREIGN KEY (staff_id) REFERENCES academic_staff(staff_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Helpful indexes for search/filter screens
CREATE INDEX idx_students_class_id ON students(class_id);
CREATE INDEX idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX idx_grades_student_id ON grades(student_id);
CREATE INDEX idx_grades_course_id ON grades(course_id);
CREATE INDEX idx_reports_staff_id ON reports(staff_id);

-- SAMPLE DATA FOR DEMO
-- Passwords are plain text only for classroom/demo because the current Flask login checks password directly.
INSERT INTO users (user_id, username, password, role) VALUES
('U001', 'admin', '123', 'Admin'),
('U002', 'staff01', '123', 'AcademicStaff'),
('U003', 'staff02', '123', 'AcademicStaff'),
('U004', 'student01', '123', 'Student'),
('U005', 'student02', '123', 'Student'),
('U006', 'student03', '123', 'Student');

INSERT INTO administrators (admin_id, user_id, full_name) VALUES
('AD001', 'U001', 'System Administrator');

INSERT INTO academic_staff (staff_id, user_id, full_name, email, phone, department) VALUES
('AS001', 'U002', 'Nguyen Van An', 'an.nguyen@school.edu.vn', '0901000001', 'Information Technology'),
('AS002', 'U003', 'Tran Thi Binh', 'binh.tran@school.edu.vn', '0901000002', 'Business Administration');

INSERT INTO courses (course_id, course_name, credits, description) VALUES
('C001', 'Database Systems', 3, 'Relational database design, SQL, normalization, and transactions.'),
('C002', 'Web Programming with Flask', 3, 'Build web applications with Python Flask, HTML, CSS, and MySQL.'),
('C003', 'Software Engineering', 3, 'Requirement analysis, system design, testing, and project management.');

INSERT INTO class_sections (class_id, staff_id, class_name) VALUES
('CL001', 'AS001', 'IT-K15A'),
('CL002', 'AS002', 'BA-K15B');

INSERT INTO students (student_id, class_id, user_id, full_name, gender, date_of_birth, address, phone, email, department) VALUES
('ST001', 'CL001', 'U004', 'Le Minh Quan', 'Male', '2004-03-12', 'Ha Noi', '0912000001', 'quan.le@student.edu.vn', 'Information Technology'),
('ST002', 'CL001', 'U005', 'Pham Ngoc Mai', 'Female', '2004-07-25', 'Da Nang', '0912000002', 'mai.pham@student.edu.vn', 'Information Technology'),
('ST003', 'CL002', 'U006', 'Hoang Anh Tuan', 'Male', '2003-11-08', 'Ho Chi Minh City', '0912000003', 'tuan.hoang@student.edu.vn', 'Business Administration');

INSERT INTO enrollments (enrollment_id, student_id, course_id, semester, status, enrollment_date) VALUES
('EN001', 'ST001', 'C001', '2025-2026 HK1', 'Registered', '2025-09-01'),
('EN002', 'ST001', 'C002', '2025-2026 HK1', 'Registered', '2025-09-01'),
('EN003', 'ST002', 'C001', '2025-2026 HK1', 'Registered', '2025-09-01'),
('EN004', 'ST002', 'C003', '2025-2026 HK1', 'Registered', '2025-09-02'),
('EN005', 'ST003', 'C002', '2025-2026 HK1', 'Registered', '2025-09-02'),
('EN006', 'ST003', 'C003', '2025-2026 HK1', 'Registered', '2025-09-02');

INSERT INTO grades (grade_id, student_id, staff_id, course_id, attendance_score, midterm_score, final_score, total_score, letter_grade) VALUES
('G001', 'ST001', 'AS001', 'C001', 9.00, 8.00, 8.50, 8.45, 'B+'),
('G002', 'ST001', 'AS001', 'C002', 9.50, 8.50, 9.00, 8.95, 'A'),
('G003', 'ST002', 'AS001', 'C001', 8.00, 7.50, 8.00, 7.90, 'B'),
('G004', 'ST003', 'AS002', 'C003', 8.50, 7.00, 7.50, 7.45, 'B');

INSERT INTO reports (report_id, staff_id, report_type, generated_date) VALUES
('R001', 'AS001', 'Grade Summary', '2025-10-15'),
('R002', 'AS002', 'Enrollment Summary', '2025-10-16');

-- Quick test queries
-- SELECT username, role FROM users;
-- SELECT s.student_id, s.full_name, c.course_name, g.total_score, g.letter_grade
-- FROM grades g
-- JOIN students s ON g.student_id = s.student_id
-- JOIN courses c ON g.course_id = c.course_id;