import sqlite3
from hashlib import sha256
from config import dbbasepath
from datetime import datetime
import os
def create_tables(email,password,nome):
    userhash = sha256(f"{email}".encode()).hexdigest()
    if os.path.exists(f"{dbbasepath}{userhash}.db"):
        return False

    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    tables = {
        "user":"CREATE TABLE user (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, password TEXT,hash TEXT, nome TEXT)",
        "logs":"CREATE TABLE logs (id INTEGER PRIMARY KEY AUTOINCREMENT, log TEXT, hash TEXT)",
        "writings":"CREATE TABLE writings (id INTEGER PRIMARY KEY AUTOINCREMENT, userhash TEXT, title TEXT, date_created DATE, date_updated DATE, hash TEXT,last_page INTEGER,paginas TEXT,capapath TEXT)"
    }
    cursor = conn.cursor()
    for table in tables:
        cursor.execute(tables[table])
    conn.commit()
    cursor.execute("INSERT INTO user (email,password,hash,nome) VALUES (?,?,?,?)",(email,password,userhash,nome))
    conn.commit()
    conn.close()
    return userhash

def start_session(email,password):
    userhash = sha256(f"{email}".encode()).hexdigest()

    if not os.path.exists(f"{dbbasepath}{userhash}.db"):
        return None

    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM user WHERE email=? AND password=?",(email,password))
        user = cursor.fetchone()
        if user:
            return user[3]
        return None
    except:
        return None

def verify_db(userhash):
    if not os.path.exists(f"{dbbasepath}{userhash}.db"):
        return False
    return True