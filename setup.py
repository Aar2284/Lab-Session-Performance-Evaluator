#!/usr/bin/env python3
"""
Setup script for Lab Performance Evaluation System
Run this after setting up your Oracle database
"""

import cx_Oracle
from db import get_connection

def test_connection():
    """Test Oracle database connection"""
    try:
        conn = get_connection()
        print("✅ Database connection successful!")
        
        # Test basic query
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM user_tables")
        table_count = cur.fetchone()[0]
        print(f"📊 Found {table_count} tables in database")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_tables():
    """Check if required tables exist"""
    required_tables = ['STUDENTS', 'LABS', 'SUBMISSIONS', 'EVALUATIONS']
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT table_name FROM user_tables")
        existing_tables = [row[0] for row in cur.fetchall()]
        
        print("\n📋 Table Status:")
        for table in required_tables:
            if table in existing_tables:
                print(f"✅ {table} - EXISTS")
            else:
                print(f"❌ {table} - MISSING")
        
        conn.close()
        return all(table in existing_tables for table in required_tables)
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False

def check_procedures():
    """Check if PL/SQL procedures and functions exist"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        # Check function
        try:
            cur.execute("SELECT get_avg_marks(1) FROM dual")
            print("✅ get_avg_marks function - EXISTS")
        except:
            print("❌ get_avg_marks function - MISSING")
        
        # Check procedure (this will show if it exists)
        cur.execute("""
            SELECT object_name FROM user_objects 
            WHERE object_type = 'PROCEDURE' 
            AND object_name = 'AUTO_EVALUATE_ALL'
        """)
        
        if cur.fetchone():
            print("✅ auto_evaluate_all procedure - EXISTS")
        else:
            print("❌ auto_evaluate_all procedure - MISSING")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error checking procedures: {e}")

def main():
    print("🧪 Lab Performance Evaluation System - Setup Check")
    print("=" * 50)
    
    # Test connection
    if not test_connection():
        print("\n❌ Setup failed: Cannot connect to database")
        print("Please check your Oracle database configuration in db.py")
        return
    
    # Check tables
    if not check_tables():
        print("\n⚠️  Some tables are missing!")
        print("Please run the schema.sql file in your Oracle database:")
        print("SQL> @schema.sql")
        return
    
    # Check procedures
    print()
    check_procedures()
    
    print("\n🎉 Setup check complete!")
    print("You can now run: python app.py")

if __name__ == "__main__":
    main()