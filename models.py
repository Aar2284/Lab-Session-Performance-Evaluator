# models.py - Oracle Database Models (Reference Only)
# This file contains the logical model structure for reference
# Actual tables are created using schema.sql

"""
Database Schema Reference:

STUDENTS:
- roll_no (VARCHAR2(20)) - Primary Key
- name (VARCHAR2(100))
- email (VARCHAR2(100))
- created_at (DATE)

LABS:
- lab_id (NUMBER) - Primary Key
- lab_name (VARCHAR2(100))
- max_marks (NUMBER)
- created_at (DATE)

SUBMISSIONS:
- submission_id (NUMBER) - Primary Key
- roll_no (VARCHAR2(20)) - Foreign Key to STUDENTS
- lab_id (NUMBER) - Foreign Key to LABS
- submitted_at (DATE)
- status (VARCHAR2(20))

EVALUATIONS:
- evaluation_id (NUMBER) - Primary Key
- submission_id (NUMBER) - Foreign Key to SUBMISSIONS
- marks (NUMBER(5,2))
- feedback (CLOB)
- evaluated_at (DATE)
- evaluation_type (VARCHAR2(20)) - 'MANUAL' or 'AUTO'
"""

# Since we're using raw Oracle SQL connections, 
# we don't need SQLAlchemy models for this project
