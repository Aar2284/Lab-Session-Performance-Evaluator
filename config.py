import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Oracle Database Configuration
    ORACLE_HOST = 'localhost'
    ORACLE_PORT = 1521
    ORACLE_SERVICE = 'XEPDB1'
    ORACLE_USER = 'lab_user'
    ORACLE_PASSWORD = 'lab_pass'
    
    # Flask Configuration
    SECRET_KEY = 'supersecretkey'
    DEBUG = True
