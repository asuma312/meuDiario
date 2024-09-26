import sqlite3
from hashlib import sha256
from config import dbbasepath
from datetime import datetime
import os

def create_perfils(userhash):
    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    cursor = conn.cursor()
    userinfo = cursor.execute("SELECT * FROM user WHERE hash=?",(userhash,)).fetchone()
    perfis = {
        "base":"INSERT INTO perfil_info(font,fontcolor,backgroundcolor) VALUES ('arial','black','white')",
        'pink':"INSERT INTO perfil_info(font,fontcolor,backgroundcolor) VALUES ('arial','white','pink')",
        'black':"INSERT INTO perfil_info(font,fontcolor,backgroundcolor) VALUES ('arial','white','black')",
    }
    for perfil in perfis:
        cursor.execute(perfis[perfil])

    perfilimages = {
        "base":{"images":["https://w7.pngwing.com/pngs/389/384/png-transparent-nickelodeon-spongebob-spreading-his-hand-bob-esponja-patrick-star-nickelodeon-television-show-others-miscellaneous-cartoon-vehicle.png"],"perfilid":1},
        "pink":{"images":["https://gallerypng.com/wp-content/uploads/2024/08/Cute-My-Melody-png-image.png"],"perfilid":2},
        "black":{"images":["https://www.pngall.com/wp-content/uploads/13/Kuromi.png"],"perfilid":3},
    }

    for perfil in perfilimages:
        for image in perfilimages[perfil]["images"]:
            cursor.execute("INSERT INTO perfil_images (imagepath,perfilinfoid) VALUES (?,?)",(image,perfilimages[perfil]["perfilid"]))
    conn.commit()
    conn.close()


def create_tables(email,password,nome):
    userhash = sha256(f"{email}".encode()).hexdigest()
    if os.path.exists(f"{dbbasepath}{userhash}.db"):
        return False

    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    tables = {
        "user":"CREATE TABLE user (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, password TEXT,hash TEXT, nome TEXT)",
        "logs":"CREATE TABLE logs (id INTEGER PRIMARY KEY AUTOINCREMENT, log TEXT, hash TEXT)",
        "writings":"CREATE TABLE writings (id INTEGER PRIMARY KEY AUTOINCREMENT, userhash TEXT, title TEXT, date_created DATE, date_updated DATE, hash TEXT,last_page INTEGER,paginas TEXT,capapath TEXT)",
        "perfil":"CREATE TABLE perfil (id INTEGER PRIMARY KEY AUTOINCREMENT,userhash TEXT, username TEXT, bio TEXT, profilepicid INTEGER, date_created DATE)",
        "perfil_info":"CREATE TABLE perfil_info (id INTEGER PRIMARY KEY AUTOINCREMENT, font TEXT, fontcolor TEXT, backgroundcolor TEXT)",
        "perfil_images":"CREATE TABLE perfil_images (id INTEGER PRIMARY KEY AUTOINCREMENT, imagepath TEXT,perfilinfoid INTEGER)",
    }
    cursor = conn.cursor()
    for table in tables:
        print(f"Creating table {table}")
        cursor.execute(tables[table])
    conn.commit()
    cursor.execute("INSERT INTO user (email,password,hash,nome) VALUES (?,?,?,?)",(email,password,userhash,nome))
    conn.commit()
    conn.close()
    create_perfils(userhash)
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