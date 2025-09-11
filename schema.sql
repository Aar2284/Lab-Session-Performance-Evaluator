-- Lab Performance Evaluation System - Oracle SQL Schema

-- Drop tables if they exist (for clean setup)
DROP TABLE evaluations CASCADE CONSTRAINTS;
DROP TABLE submissions CASCADE CONSTRAINTS;
DROP TABLE students CASCADE CONSTRAINTS;
DROP TABLE labs CASCADE CONSTRAINTS;

-- Students table
CREATE TABLE students (
    roll_no VARCHAR2(20) PRIMARY KEY,
    name VARCHAR2(100) NOT NULL,
    email VARCHAR2(100),
    created_at DATE DEFAULT SYSDATE
);

-- Labs table
CREATE TABLE labs (
    lab_id NUMBER PRIMARY KEY,
    lab_name VARCHAR2(100) NOT NULL,
    max_marks NUMBER DEFAULT 100,
    created_at DATE DEFAULT SYSDATE
);

-- Submissions table
CREATE TABLE submissions (
    submission_id NUMBER PRIMARY KEY,
    roll_no VARCHAR2(20) NOT NULL,
    lab_id NUMBER NOT NULL,
    submitted_at DATE DEFAULT SYSDATE,
    status VARCHAR2(20) DEFAULT 'SUBMITTED',
    CONSTRAINT fk_sub_student FOREIGN KEY (roll_no) REFERENCES students(roll_no),
    CONSTRAINT fk_sub_lab FOREIGN KEY (lab_id) REFERENCES labs(lab_id),
    CONSTRAINT uk_sub_unique UNIQUE (roll_no, lab_id)
);

-- Evaluations table
CREATE TABLE evaluations (
    evaluation_id NUMBER PRIMARY KEY,
    submission_id NUMBER NOT NULL,
    marks NUMBER(5,2),
    feedback CLOB,
    evaluated_at DATE DEFAULT SYSDATE,
    evaluation_type VARCHAR2(20) DEFAULT 'MANUAL', -- MANUAL or AUTO
    CONSTRAINT fk_eval_submission FOREIGN KEY (submission_id) REFERENCES submissions(submission_id)
);

-- Sequences for auto-increment
CREATE SEQUENCE seq_submission_id START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_evaluation_id START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE seq_lab_id START WITH 1 INCREMENT BY 1;

-- Triggers for auto-increment
CREATE OR REPLACE TRIGGER trg_submissions_id
    BEFORE INSERT ON submissions
    FOR EACH ROW
BEGIN
    IF :NEW.submission_id IS NULL THEN
        :NEW.submission_id := seq_submission_id.NEXTVAL;
    END IF;
END;
/

CREATE OR REPLACE TRIGGER trg_evaluations_id
    BEFORE INSERT ON evaluations
    FOR EACH ROW
BEGIN
    IF :NEW.evaluation_id IS NULL THEN
        :NEW.evaluation_id := seq_evaluation_id.NEXTVAL;
    END IF;
END;
/

CREATE OR REPLACE TRIGGER trg_labs_id
    BEFORE INSERT ON labs
    FOR EACH ROW
BEGIN
    IF :NEW.lab_id IS NULL THEN
        :NEW.lab_id := seq_lab_id.NEXTVAL;
    END IF;
END;
/

-- Sample data for testing
INSERT INTO students (roll_no, name, email) VALUES ('CS001', 'John Doe', 'john@example.com');
INSERT INTO students (roll_no, name, email) VALUES ('CS002', 'Jane Smith', 'jane@example.com');
INSERT INTO students (roll_no, name, email) VALUES ('CS003', 'Mike Johnson', 'mike@example.com');
INSERT INTO students (roll_no, name, email) VALUES ('CS004', 'Sarah Wilson', 'sarah@example.com');

INSERT INTO labs (lab_name, max_marks) VALUES ('Database Fundamentals', 100);
INSERT INTO labs (lab_name, max_marks) VALUES ('SQL Queries', 100);
INSERT INTO labs (lab_name, max_marks) VALUES ('PL/SQL Programming', 100);
INSERT INTO labs (lab_name, max_marks) VALUES ('Database Design', 100);

COMMIT;

-- PL/SQL Function to calculate average marks for a lab
CREATE OR REPLACE FUNCTION get_avg_marks(p_lab_id NUMBER)
RETURN NUMBER
IS
    v_avg_marks NUMBER(5,2);
BEGIN
    SELECT NVL(AVG(e.marks), 0)
    INTO v_avg_marks
    FROM evaluations e
    JOIN submissions s ON e.submission_id = s.submission_id
    WHERE s.lab_id = p_lab_id;
    
    RETURN v_avg_marks;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN 0;
    WHEN OTHERS THEN
        RAISE_APPLICATION_ERROR(-20001, 'Error calculating average: ' || SQLERRM);
END get_avg_marks;
/

-- PL/SQL Procedure for auto evaluation (basic implementation)
CREATE OR REPLACE PROCEDURE auto_evaluate_all
IS
    CURSOR c_submissions IS
        SELECT s.submission_id, s.roll_no, s.lab_id
        FROM submissions s
        WHERE s.submission_id NOT IN (
            SELECT e.submission_id 
            FROM evaluations e 
            WHERE e.evaluation_type = 'AUTO'
        );
    
    v_auto_marks NUMBER;
BEGIN
    FOR rec IN c_submissions LOOP
        -- Simple auto-evaluation logic (you can enhance this)
        -- For now, assign random marks between 70-95
        v_auto_marks := ROUND(DBMS_RANDOM.VALUE(70, 95), 2);
        
        INSERT INTO evaluations (submission_id, marks, feedback, evaluation_type)
        VALUES (rec.submission_id, v_auto_marks, 
                'Auto-evaluated based on submission criteria', 'AUTO');
    END LOOP;
    
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Auto evaluation completed for ' || SQL%ROWCOUNT || ' submissions');
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE_APPLICATION_ERROR(-20002, 'Auto evaluation failed: ' || SQLERRM);
END auto_evaluate_all;
/

-- Procedure to get student performance report
CREATE OR REPLACE PROCEDURE get_student_report(p_roll_no VARCHAR2)
IS
    CURSOR c_student_labs IS
        SELECT l.lab_name, e.marks, e.feedback, e.evaluated_at
        FROM labs l
        JOIN submissions s ON l.lab_id = s.lab_id
        JOIN evaluations e ON s.submission_id = e.submission_id
        WHERE s.roll_no = p_roll_no
        ORDER BY e.evaluated_at DESC;
BEGIN
    DBMS_OUTPUT.PUT_LINE('Performance Report for Student: ' || p_roll_no);
    DBMS_OUTPUT.PUT_LINE('================================================');
    
    FOR rec IN c_student_labs LOOP
        DBMS_OUTPUT.PUT_LINE('Lab: ' || rec.lab_name);
        DBMS_OUTPUT.PUT_LINE('Marks: ' || rec.marks);
        DBMS_OUTPUT.PUT_LINE('Feedback: ' || NVL(rec.feedback, 'No feedback'));
        DBMS_OUTPUT.PUT_LINE('Date: ' || TO_CHAR(rec.evaluated_at, 'DD-MON-YYYY'));
        DBMS_OUTPUT.PUT_LINE('---');
    END LOOP;
END get_student_report;
/