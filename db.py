# db.py
import cx_Oracle
import os

def get_connection():
    # Docker Oracle connection (adjust these if needed)
    host = os.getenv('ORACLE_HOST', 'localhost')
    port = os.getenv('ORACLE_PORT', '1521')
    service = os.getenv('ORACLE_SERVICE', 'XEPDB1')  # Oracle XE pluggable database
    user = os.getenv('ORACLE_USER', 'lab_user')
    password = os.getenv('ORACLE_PASSWORD', 'lab_pass')
    
    dsn = cx_Oracle.makedsn(host, port, service_name=service)
    return cx_Oracle.connect(user=user, password=password, dsn=dsn)
