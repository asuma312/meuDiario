from flask import *
from db.queries import *


authblueprint = Blueprint("auth",__name__)



@authblueprint.route("/login",methods=["POST","GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        userhash = start_session(email,password)
        if not userhash:
            return render_template("login.html",status=False,message="Usuario não encontrado")
        session["uh"] = userhash
        conn = sqlite3.connect(f"{dbbasepath}{userhash}.db")
        cursor = conn.cursor()
        perfil = cursor.execute("SELECT * FROM perfil WHERE userhash=?", (userhash,)).fetchone()
        if not perfil:
            print('creating perfil')
            cursor.execute("INSERT INTO perfil (userhash,username,bio,profilepicid,date_created) VALUES (?,?,?,?,?)",
                           (userhash, "Crie seu apelido", "Crie sua bio", 1, datetime.now()))
            conn.commit()
            perfil = cursor.execute("SELECT * FROM perfil WHERE userhash=?", (userhash,)).fetchone()
            perfilimage = cursor.execute("SELECT * FROM perfil_images WHERE id=?", (perfil[4],)).fetchone()
            perfilinfo = cursor.execute("SELECT * FROM perfil_info WHERE id=?", (perfilimage[2],)).fetchone()
            print(perfilinfo)
            conn.close()
            inject_userinfo(perfilinfo[1], perfilinfo[2], perfilinfo[3])
        return redirect(url_for("main.seusdiarios"))
    return render_template("login.html")

@authblueprint.app_context_processor
def inject_userinfo(userfont="arial",usercolor="black",backgroundcolor="white"):
    print(f"Injecting user info {userfont} {usercolor} {backgroundcolor}")
    return {
        "userfont":userfont,
        "usercolor":usercolor,
        "backgroundcolor":backgroundcolor
    }

@authblueprint.route("/register",methods=["POST","GET"])
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
        return redirect(url_for("main.seusdiarios"))
    return render_template("register.html")


@authblueprint.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))