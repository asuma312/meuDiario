from flask import *
from db.queries import *
from decorators import verifylogged
from config import dbbasepath,nosqldbpath


mainblueprint = Blueprint("main",__name__)


@mainblueprint.route("/")
def index():
    return redirect(url_for("auth.login"))



@mainblueprint.route("/seusdiarios",methods=["POST","GET"])
@verifylogged
def seusdiarios():
    userhash = session.get("uh")
    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM writings")
    writings = cursor.fetchall()
    conn.close()
    return render_template("seusdiarios.html",writings=writings)

@mainblueprint.route("/diario/<hash>/<page>",methods=["POST","GET"])
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

@mainblueprint.route("/backend/popups/getpopup",methods=["GET"])
@verifylogged
def getdiariopopup():
    popupname = request.args.get("popup")
    diariopopup = render_template(f"popups/{popupname}.html")
    return jsonify({"status":True,"html":diariopopup})

@mainblueprint.route("/perfil/me",methods=["GET"])
@verifylogged
def perfil():
    userhash = session.get("uh")
    conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
    cursor = conn.cursor()
    perfil = cursor.execute("SELECT * FROM perfil WHERE userhash=?",(userhash,)).fetchone()

    print(perfil)
    perfilimage = cursor.execute("SELECT * FROM perfil_images WHERE id=?",(perfil[4],)).fetchone()
    print(cursor.execute("select * from perfil_images").fetchall())
    perfilinfo = cursor.execute("SELECT * FROM perfil_info WHERE id=?",(perfilimage[2],)).fetchone()
    return render_template("perfil.html",perfil=perfil,perfil_image=perfilimage)

