CREATE DATABASE IF NOT EXISTS gym_management;
USE gym_management;

-- Members Table
CREATE TABLE members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    gender VARCHAR(10),
    phone VARCHAR(15),
    email VARCHAR(100),
    join_date DATE,
    membership_plan VARCHAR(50)
);

-- Trainers Table
CREATE TABLE trainers (
    trainer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    specialization VARCHAR(100),
    phone VARCHAR(15)
);

-- Plans Table
CREATE TABLE plans (
    plan_id INT AUTO_INCREMENT PRIMARY KEY,
    plan_name VARCHAR(50),
    duration_months INT,
    price DECIMAL(10,2)
);

-- Payments Table
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    amount DECIMAL(10,2),
    payment_date DATE,
    payment_method VARCHAR(50),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

-- Attendance Table
CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    date DATE,
    status VARCHAR(10),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

-- Member-Trainer Mapping
CREATE TABLE member_trainer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT,
    trainer_id INT,
    FOREIGN KEY (member_id) REFERENCES members(member_id),
    FOREIGN KEY (trainer_id) REFERENCES trainers(trainer_id)
);

-- Sample Data
INSERT INTO plans (plan_name, duration_months, price) VALUES
('Monthly', 1, 1000),
('Quarterly', 3, 2500),
('Yearly', 12, 8000);

INSERT INTO trainers (name, specialization, phone) VALUES
('Rahul', 'Weight Training', '9876543210'),
('Amit', 'Cardio', '9876501234');

INSERT INTO members (name, age, gender, phone, email, join_date, membership_plan) VALUES
('Bhavik', 22, 'Male', '9999999999', 'bhavik@gmail.com', CURDATE(), 'Monthly');

INSERT INTO payments (member_id, amount, payment_date, payment_method) VALUES
(1, 1000, CURDATE(), 'Cash');

INSERT INTO attendance (member_id, date, status) VALUES
(1, CURDATE(), 'Present');

INSERT INTO member_trainer (member_id, trainer_id) VALUES
(1, 1);