import cx_Oracle

# Connect to Oracle
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="XEPDB1")
connection = cx_Oracle.connect(user="lab_user", password="lab_pass", dsn=dsn)
cursor = connection.cursor()

def view_students():
    print("\n--- Student List ---")
    cursor.execute("SELECT roll_no, name FROM students")
    for row in cursor.fetchall():
        print(f"Roll No: {row[0]}, Name: {row[1]}")

def submit_lab():
    roll_no = input("Enter Roll No: ")
    lab_id = int(input("Enter Lab ID: "))
    try:
        cursor.execute("""
            INSERT INTO submissions (roll_no, lab_id)
            VALUES (:1, :2)
        """, (roll_no, lab_id))
        connection.commit()
        print("✅ Lab submitted.")
    except cx_Oracle.IntegrityError as e:
        print("❌ Submission failed:", e)

def auto_evaluate():
    cursor.callproc("auto_evaluate_all")
    connection.commit()
    print("✅ Auto evaluation triggered.")

def get_avg():
    try:
        lab_id = int(input("Enter Lab ID: "))
        cursor.execute("SELECT get_avg_marks(:1) FROM dual", [lab_id])
        avg = cursor.fetchone()[0]
        print(f"📊 Average Marks for Lab {lab_id}: {avg}")
    except Exception as e:
        print("❌ Error:", e)

def manual_evaluation():
    try:
        submission_id = int(input("Enter Submission ID: "))
        marks = float(input("Enter Marks: "))
        feedback = input("Enter Feedback: ")

        cursor.execute("""
            INSERT INTO evaluations (submission_id, marks, feedback)
            VALUES (:1, :2, :3)
        """, (submission_id, marks, feedback))
        connection.commit()
        print("✅ Evaluation submitted.")
    except cx_Oracle.IntegrityError as e:
        print("❌ Submission not found or already evaluated.")
    except Exception as e:
        print("❌ Error:", e)

def main():
    while True:
        print("\n--- LAB CLI ---")
        print("1. View Students")
        print("2. Submit Lab")
        print("3. Run Auto Evaluation")
        print("4. Get Avg Marks")
        print("5. Exit")
        print("6. Manual Evaluation")
        choice = input("Choose: ")

        if choice == '1':
            view_students()
        elif choice == '2':
            submit_lab()
        elif choice == '3':
            auto_evaluate()
        elif choice == '4':
            get_avg()
        elif choice == '5':
            break
        elif choice == '6':
            manual_evaluation()
        else:
            print("❓ Invalid choice.")

if __name__ == "__main__":
    m
