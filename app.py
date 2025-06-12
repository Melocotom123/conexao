from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from database.db import get_db_connection

app = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static")
app.secret_key = "chave_super_secreta"


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

        if aluno and aluno['senha'] == senha:  # Se senha tiver hash, use check_password_hash
            session["usuario"] = aluno["nome"]
            session["tipo"] = "aluno"
            return redirect(url_for("inicial_aluno"))
        else:
            flash("RA ou senha incorretos")
            return redirect(url_for("login_aluno"))
    return render_template("login_aluno.html")

@app.route("/inicial_aluno")
def inicial_aluno():
    if session.get("tipo") != "aluno":
        flash("Você precisa estar logado como aluno.")
        return redirect(url_for("login_aluno"))
    return render_template("inicial_aluno.html", nome=session["usuario"])

# Mesma ideia para os outros logins e páginas protegidas

@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da sessão.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
