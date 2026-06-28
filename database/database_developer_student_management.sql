-- Database Developer script for Student Management System
-- MySQL 8.0+
-- Tables: users, students, courses, class_sections, enrollments, grades

CREATE DATABASE IF NOT EXISTS student_management_system
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE student_management_system;

SET FOREIGN_KEY_CHECKS = 0;
DROP VIEW IF EXISTS v_student_gpa;
DROP VIEW IF EXISTS v_grade_report;
DROP VIEW IF EXISTS v_enrollment_report;
DROP TABLE IF EXISTS grades;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS class_sections;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. User table: accounts for login and role authorization
CREATE TABLE users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('ADMIN', 'TEACHER', 'STAFF', 'STUDENT') NOT NULL DEFAULT 'STUDENT',
  full_name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  phone VARCHAR(20),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Student table: student profile information
CREATE TABLE students (
  student_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT UNIQUE,
  student_code VARCHAR(20) NOT NULL UNIQUE,
  full_name VARCHAR(100) NOT NULL,
  date_of_birth DATE,
  gender ENUM('MALE', 'FEMALE', 'OTHER') DEFAULT 'OTHER',
  email VARCHAR(100) NOT NULL UNIQUE,
  phone VARCHAR(20),
  address VARCHAR(255),
  major VARCHAR(100),
  class_name VARCHAR(50),
  academic_year VARCHAR(20),
  status ENUM('ACTIVE', 'INACTIVE', 'GRADUATED') NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_students_user
    FOREIGN KEY (user_id) REFERENCES users(user_id)
    ON UPDATE CASCADE
    ON DELETE SET NULL
) ENGINE=InnoDB;

-- 3. Course table: course/catalog information
CREATE TABLE courses (
  course_id INT AUTO_INCREMENT PRIMARY KEY,
  course_code VARCHAR(20) NOT NULL UNIQUE,
  course_name VARCHAR(120) NOT NULL,
  credits TINYINT NOT NULL,
  description TEXT,
  status ENUM('ACTIVE', 'INACTIVE') NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT chk_courses_credits CHECK (credits BETWEEN 1 AND 10)
) ENGINE=InnoDB;

-- 4. ClassSection table: each opened class of a course in a semester
CREATE TABLE class_sections (
  section_id INT AUTO_INCREMENT PRIMARY KEY,
  section_code VARCHAR(30) NOT NULL UNIQUE,
  course_id INT NOT NULL,
  lecturer_user_id INT,
  semester ENUM('HK1', 'HK2', 'HK3') NOT NULL,
  academic_year VARCHAR(20) NOT NULL,
  room VARCHAR(50),
  schedule_note VARCHAR(255),
  max_students INT NOT NULL DEFAULT 40,
  status ENUM('OPEN', 'CLOSED', 'CANCELLED') NOT NULL DEFAULT 'OPEN',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_sections_course
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT fk_sections_lecturer
    FOREIGN KEY (lecturer_user_id) REFERENCES users(user_id)
    ON UPDATE CASCADE
    ON DELETE SET NULL,
  CONSTRAINT chk_sections_max_students CHECK (max_students > 0)
) ENGINE=InnoDB;

-- 5. Enrollment table: course registration/cancellation information
CREATE TABLE enrollments (
  enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  section_id INT NOT NULL,
  enrolled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status ENUM('REGISTERED', 'CANCELLED', 'COMPLETED') NOT NULL DEFAULT 'REGISTERED',
  note VARCHAR(255),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_enrollments_student
    FOREIGN KEY (student_id) REFERENCES students(student_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_enrollments_section
    FOREIGN KEY (section_id) REFERENCES class_sections(section_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT uq_enrollments_student_section UNIQUE (student_id, section_id)
) ENGINE=InnoDB;

-- 6. Grade table: grade components and calculated final grade/GPA point
CREATE TABLE grades (
  grade_id INT AUTO_INCREMENT PRIMARY KEY,
  enrollment_id INT NOT NULL UNIQUE,
  attendance_score DECIMAL(4,2) DEFAULT 0.00,
  assignment_score DECIMAL(4,2) DEFAULT 0.00,
  midterm_score DECIMAL(4,2) DEFAULT 0.00,
  final_exam_score DECIMAL(4,2) DEFAULT 0.00,
  final_score DECIMAL(4,2) GENERATED ALWAYS AS (
    ROUND(
      COALESCE(attendance_score, 0) * 0.10 +
      COALESCE(assignment_score, 0) * 0.20 +
      COALESCE(midterm_score, 0) * 0.30 +
      COALESCE(final_exam_score, 0) * 0.40,
      2
    )
  ) STORED,
  letter_grade VARCHAR(2) GENERATED ALWAYS AS (
    CASE
      WHEN ROUND(COALESCE(attendance_score, 0) * 0.10 + COALESCE(assignment_score, 0) * 0.20 + COALESCE(midterm_score, 0) * 0.30 + COALESCE(final_exam_score, 0) * 0.40, 2) >= 8.5 THEN 'A'
      WHEN ROUND(COALESCE(attendance_score, 0) * 0.10 + COALESCE(assignment_score, 0) * 0.20 + COALESCE(midterm_score, 0) * 0.30 + COALESCE(final_exam_score, 0) * 0.40, 2) >= 8.0 THEN 'B+'
      WHEN ROUND(COALESCE(attendance_score, 0) * 0.10 + COALESCE(assignment_score, 0) * 0.20 + COALESCE(midterm_score, 0) * 0.30 + COALESCE(final_exam_score, 0) * 0.40, 2) >= 7.0 THEN 'B'
      WHEN ROUND(COALESCE(attendance_score, 0) * 0.10 + COALESCE(assignment_score, 0) * 0.20 + COALESCE(midterm_score, 0) * 0.30 + COALESCE(final_exam_score, 0) * 0.40, 2) >= 6.5 THEN 'C+'
      WHEN ROUND(COALESCE(attendance_score, 0) * 0.10 + COALESCE(assignment_score, 0) * 0.20 + COALESCE(midterm_score, 0) * 0.30 + COALESCE(final_exam_score, 0) * 0.40, 2) >= 5.5 THEN 'C'
      WHEN ROUND(COALESCE(attendance_score, 0) * 0.10 + COALESCE(assignment_score, 0) * 0.20 + COALESCE(midterm_score, 0) * 0.30 + COALESCE(final_exam_score, 0) * 0.40, 2) >= 5.0 THEN 'D+'
      WHEN ROUND(COALESCE(attendance_score, 0) * 0.10 + COALESCE(assignment_score, 0) * 0.20 + COALESCE(midterm_score, 0) * 0.30 + COALESCE(final_exam_score, 0) * 0.40, 2) >= 4.0 THEN 'D'
      ELSE 'F'
    END
  ) STORED,
  grade_point DECIMAL(3,2) GENERATED ALWAYS AS (
    CASE
      WHEN ROUND(COALESCE(attendance_score, 0) * 0.10 + COALESCE(assignment_score, 0) * 0.20 + COALESCE(midterm_score, 0) * 0.30 + COALESCE(final_exam_score, 0) * 0.40, 2) >= 8.5 THEN 4.00
      WHEN ROUND(COALESCE(attendance_score, 0) * 0.10 + COALESCE(assignment_score, 0) * 0.20 + COALESCE(midterm_score, 0) * 0.30 + COALESCE(final_exam_score, 0) * 0.40, 2) >= 8.0 THEN 3.50
      WHEN ROUND(COALESCE(attendance_score, 0) * 0.10 + COALESCE(assignment_score, 0) * 0.20 + COALESCE(midterm_score, 0) * 0.30 + COALESCE(final_exam_score, 0) * 0.40, 2) >= 7.0 THEN 3.00
      WHEN ROUND(COALESCE(attendance_score, 0) * 0.10 + COALESCE(assignment_score, 0) * 0.20 + COALESCE(midterm_score, 0) * 0.30 + COALESCE(final_exam_score, 0) * 0.40, 2) >= 6.5 THEN 2.50
      WHEN ROUND(COALESCE(attendance_score, 0) * 0.10 + COALESCE(assignment_score, 0) * 0.20 + COALESCE(midterm_score, 0) * 0.30 + COALESCE(final_exam_score, 0) * 0.40, 2) >= 5.5 THEN 2.00
      WHEN ROUND(COALESCE(attendance_score, 0) * 0.10 + COALESCE(assignment_score, 0) * 0.20 + COALESCE(midterm_score, 0) * 0.30 + COALESCE(final_exam_score, 0) * 0.40, 2) >= 5.0 THEN 1.50
      WHEN ROUND(COALESCE(attendance_score, 0) * 0.10 + COALESCE(assignment_score, 0) * 0.20 + COALESCE(midterm_score, 0) * 0.30 + COALESCE(final_exam_score, 0) * 0.40, 2) >= 4.0 THEN 1.00
      ELSE 0.00
    END
  ) STORED,
  remarks VARCHAR(255),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_grades_enrollment
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT chk_grades_attendance CHECK (attendance_score BETWEEN 0 AND 10),
  CONSTRAINT chk_grades_assignment CHECK (assignment_score BETWEEN 0 AND 10),
  CONSTRAINT chk_grades_midterm CHECK (midterm_score BETWEEN 0 AND 10),
  CONSTRAINT chk_grades_final_exam CHECK (final_exam_score BETWEEN 0 AND 10)
) ENGINE=InnoDB;

-- Indexes for faster searching and reporting
CREATE INDEX idx_students_code_name ON students(student_code, full_name);
CREATE INDEX idx_courses_code_name ON courses(course_code, course_name);
CREATE INDEX idx_sections_course_semester ON class_sections(course_id, semester, academic_year);
CREATE INDEX idx_enrollments_student_status ON enrollments(student_id, status);
CREATE INDEX idx_enrollments_section_status ON enrollments(section_id, status);

-- Demo data
-- password_hash is only a demo value. In Flask, store hashes generated by werkzeug.security.generate_password_hash.
INSERT INTO users (user_id, username, password_hash, role, full_name, email, phone) VALUES
(1, 'admin', 'demo_hash_123456', 'ADMIN', 'System Admin', 'admin@example.com', '0900000001'),
(2, 'teacher01', 'demo_hash_123456', 'TEACHER', 'Nguyen Huu Thuan', 'teacher01@example.com', '0900000002'),
(3, 'staff01', 'demo_hash_123456', 'STAFF', 'Huynh Ngoc Phong', 'staff01@example.com', '0900000003'),
(4, 'sv001', 'demo_hash_123456', 'STUDENT', 'Tran Van An', 'an@example.com', '0900000004'),
(5, 'sv002', 'demo_hash_123456', 'STUDENT', 'Le Thi Binh', 'binh@example.com', '0900000005'),
(6, 'sv003', 'demo_hash_123456', 'STUDENT', 'Pham Minh Chau', 'chau@example.com', '0900000006');

INSERT INTO students (student_id, user_id, student_code, full_name, date_of_birth, gender, email, phone, address, major, class_name, academic_year) VALUES
(1, 4, 'SV001', 'Tran Van An', '2005-03-15', 'MALE', 'an@example.com', '0900000004', 'Ho Chi Minh City', 'Information Technology', '22DTHA1', '2022-2026'),
(2, 5, 'SV002', 'Le Thi Binh', '2005-07-20', 'FEMALE', 'binh@example.com', '0900000005', 'Ho Chi Minh City', 'Information Technology', '22DTHA1', '2022-2026'),
(3, 6, 'SV003', 'Pham Minh Chau', '2005-11-02', 'OTHER', 'chau@example.com', '0900000006', 'Ho Chi Minh City', 'Information Technology', '22DTHA2', '2022-2026');

INSERT INTO courses (course_id, course_code, course_name, credits, description) VALUES
(1, 'IT101', 'Introduction to Programming', 3, 'Basic programming concepts'),
(2, 'DB201', 'Database Systems', 3, 'Relational database design and SQL'),
(3, 'WEB301', 'Web Application Development', 3, 'Web development with Flask'),
(4, 'SE401', 'Software Engineering', 4, 'Software process and project management');

INSERT INTO class_sections (section_id, section_code, course_id, lecturer_user_id, semester, academic_year, room, schedule_note, max_students, status) VALUES
(1, 'IT101-HK1-2025-A', 1, 2, 'HK1', '2025-2026', 'A101', 'Mon 07:30-09:30', 45, 'OPEN'),
(2, 'DB201-HK1-2025-A', 2, 2, 'HK1', '2025-2026', 'B203', 'Wed 09:30-11:30', 40, 'OPEN'),
(3, 'WEB301-HK1-2025-A', 3, 2, 'HK1', '2025-2026', 'C305', 'Fri 13:00-15:00', 35, 'OPEN'),
(4, 'SE401-HK1-2025-A', 4, 2, 'HK1', '2025-2026', 'D401', 'Tue 13:00-16:00', 35, 'OPEN');

INSERT INTO enrollments (enrollment_id, student_id, section_id, status, note) VALUES
(1, 1, 1, 'COMPLETED', 'Demo enrollment'),
(2, 1, 2, 'COMPLETED', 'Demo enrollment'),
(3, 1, 3, 'REGISTERED', 'Currently studying'),
(4, 2, 1, 'COMPLETED', 'Demo enrollment'),
(5, 2, 2, 'COMPLETED', 'Demo enrollment'),
(6, 3, 1, 'REGISTERED', 'Currently studying'),
(7, 3, 3, 'REGISTERED', 'Currently studying');

INSERT INTO grades (enrollment_id, attendance_score, assignment_score, midterm_score, final_exam_score, remarks) VALUES
(1, 9.00, 8.50, 8.00, 8.75, 'Good'),
(2, 8.00, 7.50, 7.00, 7.25, 'Passed'),
(4, 9.50, 9.00, 8.50, 9.00, 'Very good'),
(5, 7.00, 6.50, 6.00, 6.25, 'Passed');

-- Report views
CREATE VIEW v_enrollment_report AS
SELECT
  e.enrollment_id,
  s.student_code,
  s.full_name AS student_name,
  c.course_code,
  c.course_name,
  cs.section_code,
  cs.semester,
  cs.academic_year,
  e.status AS enrollment_status,
  e.enrolled_at
FROM enrollments e
JOIN students s ON e.student_id = s.student_id
JOIN class_sections cs ON e.section_id = cs.section_id
JOIN courses c ON cs.course_id = c.course_id;

CREATE VIEW v_grade_report AS
SELECT
  s.student_code,
  s.full_name AS student_name,
  c.course_code,
  c.course_name,
  c.credits,
  cs.section_code,
  g.attendance_score,
  g.assignment_score,
  g.midterm_score,
  g.final_exam_score,
  g.final_score,
  g.letter_grade,
  g.grade_point,
  e.status AS enrollment_status
FROM grades g
JOIN enrollments e ON g.enrollment_id = e.enrollment_id
JOIN students s ON e.student_id = s.student_id
JOIN class_sections cs ON e.section_id = cs.section_id
JOIN courses c ON cs.course_id = c.course_id;

CREATE VIEW v_student_gpa AS
SELECT
  s.student_id,
  s.student_code,
  s.full_name AS student_name,
  ROUND(SUM(g.grade_point * c.credits) / NULLIF(SUM(c.credits), 0), 2) AS gpa_4_scale,
  ROUND(SUM(g.final_score * c.credits) / NULLIF(SUM(c.credits), 0), 2) AS average_10_scale,
  SUM(c.credits) AS completed_credits
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN grades g ON e.enrollment_id = g.enrollment_id
JOIN class_sections cs ON e.section_id = cs.section_id
JOIN courses c ON cs.course_id = c.course_id
WHERE e.status = 'COMPLETED'
GROUP BY s.student_id, s.student_code, s.full_name;

-- Useful demo queries
-- SELECT * FROM v_enrollment_report;
-- SELECT * FROM v_grade_report;
-- SELECT * FROM v_student_gpa;
