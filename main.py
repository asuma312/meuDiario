from flask import *
import sqlite3
from db.queries import *
from decorators import verifylogged
from config import dbbasepath,nosqldbpath
from hashlib import sha256
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = "1234567890"


def delete_writing_pages(hash):
    files = os.listdir(f"{nosqldbpath}")
    hashpages = [file for file in files if file.startswith(hash) and file.endswith(".json")]
    for pages in hashpages:
        os.remove(f"{nosqldbpath}{pages}")
    hashfolders = [file for file in files if file.startswith(hash) and os.path.isdir(f"{nosqldbpath}{file}")]
    for folder in hashfolders:
        files = os.listdir(f"{nosqldbpath}{folder}")
        for file in files:
            os.remove(f"{nosqldbpath}{folder}/{file}")
        os.rmdir(f"{nosqldbpath}{folder}")

def delete_specific_page(hash,page):
    files = os.listdir(f"{nosqldbpath}")
    hashpages = [file for file in files if file.startswith(hash) and file.endswith(".json") and file.split("_")[1].split(".")[0] == page]
    for pages in hashpages:
        os.remove(f"{nosqldbpath}{pages}")
    hashfolders = [file for file in files if file.startswith(hash) and os.path.isdir(f"{nosqldbpath}{file}")]


@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login",methods=["POST","GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        userhash = start_session(email,password)
        if not userhash:
            return render_template("login.html",status=False,message="Usuario não encontrado")
        session["uh"] = userhash
        return redirect(url_for("seusdiarios"))
    return render_template("login.html")

@app.route("/register",methods=["POST","GET"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        nome = request.form.get("nome")
        if not email or not password:
            return render_template("register.html",status=False,message="Parametros inválidos")
        userhash = create_tables(email,password,nome)
        if not userhash:
            return render_template("register.html",status=False,message="Usuario já existe")


        session["uh"] = userhash
        return redirect(url_for("seusdiarios"))
    return render_template("register.html")

@app.route("/seusdiarios",methods=["POST","GET"])
@verifylogged
def seusdiarios():
    userhash = session.get("uh")
    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM writings")
    writings = cursor.fetchall()
    conn.close()
    return render_template("seusdiarios.html",writings=writings)

@app.route("/diario/<hash>/<page>",methods=["POST","GET"])
@verifylogged
def diario(hash,page):
    userhash = session.get("uh")
    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    cursor = conn.cursor()
    userid = cursor.execute("SELECT * FROM user WHERE hash=?",(userhash,)).fetchone()[0]
    if not userid:
        return redirect(url_for("logout"))
    cursor.execute("SELECT * FROM writings WHERE hash=? AND userhash=?",(hash,userhash))
    writing = cursor.fetchone()
    if not writing:
        return redirect(url_for("seusdiarios"))
    nomediario = writing[2]
    pages = str(writing[7]).split(",")
    lastpage = writing[6]
    nextpage = [int(p) for p in pages if int(p) > int(page)][0] if len(pages)>1 and int(page) < lastpage else None
    prevpage = [int(p) for p in pages if int(p) < int(page)][-1] if len(pages)>1  and int(page) > 1 else None

    capa = writing[8]

    return render_template("diario.html",writing=writing,nextpage=nextpage,hash=hash,prevpage=prevpage,page=page,nomediario=nomediario,capa=capa)

@app.route("/backend/popups/newdiariopopup",methods=["GET"])
@verifylogged
def getdiariopopup():
    diariopopup = render_template("popups/novodiario.html")
    return jsonify({"status":True,"html":diariopopup})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/api/createwriting",methods=["POST"])
@verifylogged
def createwriting():
    userhash = session.get("uh")
    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    cursor = conn.cursor()
    title = request.get_json().get("title")
    timenow = datetime.now()
    hashstring = f"{title}{userhash}{timenow}"
    datacriado = datetime.now()
    ultima_modificacao = datetime.now()
    hash = sha256(hashstring.encode()).hexdigest()
    lastpage = 1
    paginas = "1"

    cursor.execute("INSERT INTO writings (title,date_created,date_updated,hash,userhash,last_page,paginas) VALUES (?,?,?,?,?,?,?)",(title,datacriado,ultima_modificacao,hash,userhash,lastpage,paginas))
    conn.commit()
    conn.close()
    return jsonify({"status":True,"message":"Writing created","url":url_for("diario",hash=hash,page=1)})


@app.route("/api/changewriting",methods=["POST"])
@verifylogged
def changewriting():
    userhash = session.get("uh")
    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    cursor = conn.cursor()
    _json = request.get_json()
    title = _json.get("title")
    hash = _json.get("hash")
    cursor.execute("UPDATE writings SET title=? WHERE hash=? AND userhash=?",(title,hash,userhash))
    conn.commit()
    conn.close()
    return jsonify({"status":True,"message":"Writing updated"})

@app.route("/api/deletewriting",methods=["POST"])
@verifylogged
def deletewriting():
    userhash = session.get("uh")
    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    cursor = conn.cursor()
    _json = request.get_json()
    hash = _json.get("hash")
    cursor.execute("DELETE FROM writings WHERE hash=? AND userhash=?",(hash,userhash))
    conn.commit()
    conn.close()
    delete_writing_pages(hash)
    return jsonify({"status":True,"message":"Writing deleted"})



@app.route("/api/salvar",methods=["POST"])
@verifylogged
def savewriting():
    userhash = session.get("uh")
    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    if not conn:
        return jsonify({"status":False,"message":"Database not found"})
    cursor = conn.cursor()
    _json = request.get_json()
    hash = _json.get("hash")
    pagina = _json.get("pagina")
    writing = cursor.execute("SELECT * FROM writings WHERE hash=? AND userhash=?",(hash,userhash)).fetchone()
    if not writing:
        return jsonify({"status":False,"message":"Writing not found"})
    html = _json.get("html")
    content = _json.get("content")
    datadict = {
        "html":html,
        "content":content
    }
    with open(f"{nosqldbpath}{hash}_{pagina}.json","w") as f:
        json.dump(datadict,f)
    cursor.execute("UPDATE writings SET date_updated=?,last_page=? WHERE hash=? AND userhash=?",(datetime.now(),pagina,hash,userhash))
    conn.commit()
    conn.close()
    return jsonify({"status":True,"message":"Writing saved"})

@app.route("/api/getwriting",methods=["POST"])
@verifylogged
def getwriting():
    userhash = session.get("uh")
    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    cursor = conn.cursor()
    _json = request.get_json()
    hash = _json.get("hash")
    pagina = _json.get("pagina")
    writing = cursor.execute("SELECT * FROM writings WHERE hash=? AND userhash=?",(hash,userhash)).fetchone()
    if not writing:
        return jsonify({"status":False,"message":"Writing not found"})

    if not os.path.exists(f"{nosqldbpath}{hash}_{pagina}.json"):
        with open(f"{nosqldbpath}{hash}_{pagina}.json","w") as f:
            json.dump({"html":"<p></p>","content":""},f)

    with open(f"{nosqldbpath}{hash}_{pagina}.json","r") as f:
        data = json.load(f)
    return jsonify({"status":True,"data":data})


@app.route("/api/savefiles", methods=["POST"])
@verifylogged
def savefiles():
    userhash = session.get("uh")
    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    cursor = conn.cursor()

    hash = request.form.get("hash")
    writing = cursor.execute("SELECT * FROM writings WHERE hash=? AND userhash=?", (hash, userhash)).fetchone()
    if not writing:
        return jsonify({"status": False, "message": "Writing not found"})

    filepath = f"{nosqldbpath}/files/{hash}"
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    files = request.files.getlist("file")
    for file in files:
        filename = file.filename
        file.save(os.path.join(filepath, filename))

    return jsonify({"status": True, "message": "Files saved"})

@app.route("/api/getfile",methods=["POST"])
@verifylogged
def getfile():
    userhash = session.get("uh")
    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    cursor = conn.cursor()
    _json = request.get_json()
    hash = _json.get("hash")
    filename = _json.get("filename")
    writing = cursor.execute("SELECT * FROM writings WHERE hash=? AND userhash=?",(hash,userhash)).fetchone()
    if not writing:
        return jsonify({"status":False,"message":"Writing not found"})
    filepath = f"{nosqldbpath}/files/{hash}/{filename}"
    if not os.path.exists(filepath):
        return jsonify({"status":False,"message":"File not found"})
    with open(filepath) as f:
        content = f.read()
    return jsonify({"status":True,"content":content})

@app.route("/api/deletefile",methods=["POST"])
@verifylogged
def deletefile():
    userhash = session.get("uh")
    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    cursor = conn.cursor()
    _json = request.get_json()
    hash = _json.get("hash")
    filename = _json.get("filename")
    writing = cursor.execute("SELECT * FROM writings WHERE hash=? AND userhash=?",(hash,userhash)).fetchone()
    if not writing:
        return jsonify({"status":False,"message":"Writing not found"})
    filepath = f"{nosqldbpath}/files/{hash}/{filename}"
    if not os.path.exists(filepath):
        return jsonify({"status":False,"message":"File not found"})
    os.remove(filepath)
    return jsonify({"status":True,"message":"File deleted"})


@app.route("/api/newpage",methods=["POST"])
@verifylogged
def newpage():
    userhash = session.get("uh")
    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    cursor = conn.cursor()
    _json = request.get_json()
    hash = _json.get("hash")
    writing = cursor.execute("SELECT * FROM writings WHERE hash=? AND userhash=?",(hash,userhash)).fetchone()
    if not writing:
        return jsonify({"status":False,"message":"Writing not found"})
    lastpage = writing[6]
    paginas = str(writing[7]).split(",")
    paginas.append(str(int(lastpage)+1))
    paginas = ",".join(paginas)
    cursor.execute("UPDATE writings SET last_page=?,paginas=? WHERE hash=? AND userhash=?",(int(lastpage)+1,paginas,hash,userhash))
    conn.commit()
    conn.close()
    return jsonify({"status":True,"message":"New page created","page":lastpage+1})

@app.route("/api/deletepage",methods=["POST"])
@verifylogged
def deletepage():
    userhash = session.get("uh")
    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    cursor = conn.cursor()
    _json = request.get_json()
    hash = _json.get("hash")
    page = _json.get("page")
    writing = cursor.execute("SELECT * FROM writings WHERE hash=? AND userhash=?",(hash,userhash)).fetchone()
    if not writing:
        return jsonify({"status":False,"message":"Writing not found"})
    lastpage = writing[6]
    paginas = str(writing[7]).split(",")
    if page in paginas:
        paginas.remove(str(page))
        paginas = ",".join(paginas)
        cursor.execute("UPDATE writings SET last_page=?,paginas=? WHERE hash=? AND userhash=?",(lastpage-1,paginas,hash,userhash))
        conn.commit()
        conn.close()

    delete_specific_page(hash,page)
    paginas = str(writing[7]).split(",")
    prevpage = [int(p) for p in paginas if int(p) < int(page)][-1] if [int(p) for p in paginas if int(p) < int(page)] and int(page) > 1 else 1
    return jsonify({"status":True,"message":"Page deleted","page":lastpage-1,"prevurl":url_for("diario",hash=hash,page=prevpage)})

@app.route("/api/changecapa",methods=["POST"])
@verifylogged
def changecapa():
    userhash = session.get("uh")
    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    cursor = conn.cursor()
    _json = request.form
    hash = _json.get("hash")
    capafile = request.files.get("capa")

    writer = cursor.execute("SELECT * FROM writings WHERE hash=? AND userhash=?",(hash,userhash)).fetchone()
    if not writer:
        return jsonify({"status":False,"message":"Writing not found"})

    capapath = current_app.static_folder + f'/images/users/{userhash}'
    if not os.path.exists(capapath):
        os.makedirs(capapath)
    capafile.save(f"{capapath}/capa.png")
    capapath = url_for('static', filename=f'images/users/{userhash}/capa.png')

    cursor.execute("UPDATE writings SET capapath=? WHERE hash=? AND userhash=?",(capapath,hash,userhash))
    conn.commit()
    conn.close()
    return jsonify({"status":True,"message":"Capa changed","url":capapath})

if __name__ == "__main__":
    app.run(debug=True)