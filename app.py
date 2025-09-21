# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from db import get_connection

app = Flask(__name__)
app.secret_key = "supersecret"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/students")
def students():
    data = []
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT roll_no, name FROM students ORDER BY roll_no")
        data = cur.fetchall()
        conn.close()
    except Exception as e:
        flash(f"❌ Error loading students: {str(e)}", "danger")
    return render_template("students.html", students=data)

@app.route("/submit", methods=["GET", "POST"])
def submit():
    students = []
    labs = []
    
    # Get students and labs for dropdowns
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT roll_no, name FROM students ORDER BY roll_no")
        students = cur.fetchall()
        cur.execute("SELECT lab_id, lab_name FROM labs ORDER BY lab_id")
        labs = cur.fetchall()
        conn.close()
    except Exception as e:
        flash(f"❌ Error loading data: {str(e)}", "danger")
    
    if request.method == "POST":
        roll_no = request.form["roll_no"]
        lab_id = request.form["lab_id"]
        
        if not roll_no or not lab_id:
            flash("❌ Please fill in all fields!", "danger")
            return redirect(url_for("submit"))
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # Check if student exists
            cur.execute("SELECT COUNT(*) FROM students WHERE roll_no = :1", (roll_no,))
            if cur.fetchone()[0] == 0:
                flash(f"❌ Student with Roll No '{roll_no}' not found!", "danger")
                conn.close()
                return redirect(url_for("submit"))
            
            # Check if lab exists
            cur.execute("SELECT COUNT(*) FROM labs WHERE lab_id = :1", (lab_id,))
            if cur.fetchone()[0] == 0:
                flash(f"❌ Lab with ID '{lab_id}' not found!", "danger")
                conn.close()
                return redirect(url_for("submit"))
            
            # Check if already submitted
            cur.execute("SELECT COUNT(*) FROM submissions WHERE roll_no = :1 AND lab_id = :2", (roll_no, lab_id))
            if cur.fetchone()[0] > 0:
                flash(f"❌ Student '{roll_no}' has already submitted Lab {lab_id}!", "warning")
                conn.close()
                return redirect(url_for("submit"))
            
            # Insert submission
            cur.execute("INSERT INTO submissions (roll_no, lab_id) VALUES (:1, :2)", (roll_no, lab_id))
            conn.commit()
            flash("✅ Lab submitted successfully!", "success")
            
        except Exception as e:
            flash(f"❌ Database Error: {str(e)}", "danger")
        finally:
            conn.close()
        return redirect(url_for("submit"))
    
    return render_template("submit.html", students=students, labs=labs)

@app.route("/auto-evaluate")
def auto_evaluate():
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Check if there are any ungraded submissions
        cur.execute("""
            SELECT COUNT(*) FROM submissions s
            LEFT JOIN evaluations e ON s.submission_id = e.submission_id
            WHERE e.submission_id IS NULL
        """)
        ungraded_count = cur.fetchone()[0]
        
        if ungraded_count == 0:
            flash("ℹ️ No ungraded submissions found!", "info")
        else:
            cur.callproc("auto_evaluate_all")
            conn.commit()
            flash(f"✅ Auto-evaluation completed for {ungraded_count} submissions!", "success")
        
        conn.close()
    except Exception as e:
        flash(f"❌ Auto-evaluation failed: {str(e)}", "danger")
    
    return redirect(url_for("index"))

@app.route("/avg", methods=["GET", "POST"])
def avg():
    avg_marks = None
    labs = []
    
    # Get labs for dropdown
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT lab_id, lab_name FROM labs ORDER BY lab_id")
        labs = cur.fetchall()
        conn.close()
    except Exception as e:
        flash(f"❌ Error loading labs: {str(e)}", "danger")
    
    if request.method == "POST":
        lab_id = request.form["lab_id"]
        
        if not lab_id:
            flash("❌ Please select a lab!", "danger")
            return redirect(url_for("avg"))
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # Check if lab exists
            cur.execute("SELECT COUNT(*) FROM labs WHERE lab_id = :1", (lab_id,))
            if cur.fetchone()[0] == 0:
                flash(f"❌ Lab with ID '{lab_id}' not found!", "danger")
                conn.close()
                return redirect(url_for("avg"))
            
            # Get average marks
            cur.execute("SELECT get_avg_marks(:1) FROM dual", (lab_id,))
            avg_marks = cur.fetchone()[0]
            
            if avg_marks == 0:
                flash(f"ℹ️ No evaluations found for Lab {lab_id}", "info")
            else:
                flash(f"📊 Average calculated successfully!", "success")
            
            conn.close()
        except Exception as e:
            flash(f"❌ Error calculating average: {str(e)}", "danger")
    
    return render_template("avg.html", avg=avg_marks, labs=labs)

@app.route("/evaluate", methods=["GET", "POST"])
def evaluate():
    submissions = []
    if request.method == "GET":
        # Get ungraded submissions
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT s.submission_id, s.roll_no, l.lab_name, s.submitted_at
            FROM submissions s
            JOIN labs l ON s.lab_id = l.lab_id
            LEFT JOIN evaluations e ON s.submission_id = e.submission_id
            WHERE e.submission_id IS NULL
            ORDER BY s.submitted_at DESC
        """)
        submissions = cur.fetchall()
        conn.close()
    
    elif request.method == "POST":
        submission_id = request.form["submission_id"]
        marks = request.form["marks"]
        feedback = request.form["feedback"]
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO evaluations (submission_id, marks, feedback, evaluation_type)
                VALUES (:1, :2, :3, 'MANUAL')
            """, (submission_id, marks, feedback))
            conn.commit()
            flash("✅ Evaluation submitted successfully!", "success")
        except Exception as e:
            flash(f"❌ Error: {str(e)}", "danger")
        finally:
            conn.close()
        return redirect(url_for("evaluate"))
    
    return render_template("evaluate.html", submissions=submissions)

@app.route("/manage", methods=["GET", "POST"])
def manage():
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "add_student":
            roll_no = request.form["roll_no"].strip()
            name = request.form["name"].strip()
            email = request.form.get("email", "").strip()
            
            if not roll_no or not name:
                flash("❌ Roll No and Name are required!", "danger")
                return redirect(url_for("manage"))
            
            try:
                conn = get_connection()
                cur = conn.cursor()
                
                # Check if student already exists
                cur.execute("SELECT COUNT(*) FROM students WHERE roll_no = :1", (roll_no,))
                if cur.fetchone()[0] > 0:
                    flash(f"❌ Student with Roll No '{roll_no}' already exists!", "warning")
                else:
                    cur.execute("INSERT INTO students (roll_no, name, email) VALUES (:1, :2, :3)", 
                              (roll_no, name, email if email else None))
                    conn.commit()
                    flash(f"✅ Student '{name}' added successfully!", "success")
                
                conn.close()
            except Exception as e:
                flash(f"❌ Error adding student: {str(e)}", "danger")
        
        elif action == "add_lab":
            lab_name = request.form["lab_name"].strip()
            max_marks = request.form.get("max_marks", "100")
            
            if not lab_name:
                flash("❌ Lab name is required!", "danger")
                return redirect(url_for("manage"))
            
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("INSERT INTO labs (lab_name, max_marks) VALUES (:1, :2)", 
                          (lab_name, int(max_marks)))
                conn.commit()
                flash(f"✅ Lab '{lab_name}' added successfully!", "success")
                conn.close()
            except Exception as e:
                flash(f"❌ Error adding lab: {str(e)}", "danger")
        
        return redirect(url_for("manage"))
    
    # Get current students and labs
    students = []
    labs = []
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT roll_no, name, email FROM students ORDER BY roll_no")
        students = cur.fetchall()
        cur.execute("SELECT lab_id, lab_name, max_marks FROM labs ORDER BY lab_id")
        labs = cur.fetchall()
        conn.close()
    except Exception as e:
        flash(f"❌ Error loading data: {str(e)}", "danger")
    
    return render_template("manage.html", students=students, labs=labs)

if __name__ == "__main__":
    app.run(debug=True)
