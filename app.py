from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static")
app.secret_key = "chave_super_secreta"


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vergil1@",
        database="ATP3"
    )

@app.route("/testar_conexao")
def testar_conexao():
    try:
        conn = get_db_connection()
        conn.close()
        return "✅ Conexão com o banco funcionando!"
    except Exception as e:
        return f"❌ Erro: {e}"


@app.route("/")
def index():
    return render_template("index.html")

# --- LOGIN ALUNO ---
@app.route("/login/aluno", methods=["GET", "POST"])
def login_aluno():
    if request.method == "POST":
        ra = request.form["ra"]
        senha = request.form["senha"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Alunos WHERE ra = %s", (ra,))
        aluno = cursor.fetchone()
        cursor.close()
        conn.close()

        if aluno and aluno['senha'] == senha:
            session["usuario"] = aluno["nome"]
            session["tipo"] = "aluno"
            return redirect(url_for("inicial_aluno"))
        else:
            flash("RA ou senha incorretos")
    return render_template("login_aluno.html")


# --- LOGIN PROFESSOR ---
@app.route("/login/professor", methods=["GET", "POST"])
def login_professor():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Professores WHERE email = %s", (email,))
        professor = cursor.fetchone()
        cursor.close()
        conn.close()

        if professor and professor['senha'] == senha:
            session["usuario"] = professor["nome"]
            session["tipo"] = "professor"
            return redirect(url_for("inicial_professor"))
        else:
            flash("Email ou senha incorretos")
    return render_template("login_professor.html")


# --- LOGIN ADMIN ---
@app.route("/login/admin", methods=["GET", "POST"])
def login_admin():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Administradores WHERE email = %s", (email,))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()

        if admin and admin['senha'] == senha:
            session["usuario"] = admin["nome"]
            session["tipo"] = "admin"
            return redirect(url_for("dashboard_admin"))
        else:
            flash("Email ou senha incorretos")
    return render_template("login_admin.html")

@app.route("/inicial_aluno")
def inicial_aluno():
    if session.get("tipo") != "aluno":
        return redirect(url_for("index"))
    return render_template("inicial_aluno.html", nome=session["usuario"])

@app.route("/dashboard_admin")
def dashboard_admin():
    if session.get("tipo") != "admin":
        return redirect(url_for("index"))
    return f"<h2>Bem-vindo, {session['usuario']} (admin)</h2>"

@app.route("/inicial_professor")
def inicial_professor():
    if session.get("tipo") != "professor":
        return redirect(url_for("index"))
    return render_template("inicial_professor.html", nome=session["usuario"])

@app.route("/registro_professor")
def registro_professor():
    if session.get("tipo") != "professor":
        return redirect(url_for("index"))
    return render_template("registro_professor.html", nome=session["usuario"])

@app.route("/presenca_professor")
def presenca_professor():
    if session.get("tipo") != "professor":
        return redirect(url_for("index"))
    return render_template("presenca_professor.html", nome=session["usuario"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
