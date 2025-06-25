from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pymysql
import cv2
import numpy as np
import face_recognition
import joblib
from base64 import b64decode


app = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static")
app.secret_key = "chave_super_secreta"

# --- Carregar modelo de reconhecimento facial ---
clf = joblib.load("modelo_reconhecimento.pkl")

# --- Conexão com o banco ---
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="password",
        database="ATP3",
        cursorclass=pymysql.cursors.DictCursor
    )

# --- Processamento de imagem facial ---
def process_image(frame_bytes):
    nparr = np.frombuffer(frame_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    localizacoes = face_recognition.face_locations(rgb)
    codificacoes = face_recognition.face_encodings(rgb, localizacoes)

    resultados = []
    for encoding, loc in zip(codificacoes, localizacoes):
        prob = clf.predict_proba([encoding]).max()
        nome = clf.predict([encoding])[0] if prob > 0.7 else "Desconhecido"
        resultados.append({"nome": nome, "probabilidade": round(float(prob), 2)})

    return resultados

# --- Teste de conexão com o banco ---
@app.route("/testar_conexao")
def testar_conexao():
    try:
        conn = get_db_connection()
        conn.close()
        return None
    except Exception as e:
        return None

# --- Página inicial ---
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
        cursor = conn.cursor()
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
        cursor = conn.cursor()
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
        cursor = conn.cursor()
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

# --- Telas principais por tipo de usuário ---
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

# --- Telas de registro/presença ---
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

@app.route("/registro_aluno")
def registro_aluno():
    if session.get("tipo") != "aluno":
        return redirect(url_for("index"))
    return render_template("registro_aluno.html", nome=session.get("usuario"))

@app.route("/presenca_aluno")
def presenca_aluno():
    if session.get("tipo") != "aluno":
        return redirect(url_for("index"))
    return render_template("presenca_aluno.html", nome=session.get("usuario"))

# --- Rota nova para reconhecimento facial separado ---
@app.route('/reconhecimento_professor')
def reconhecimento_professor():
    return render_template('reconhecimento.html')

@app.route('/reconhecer', methods=['POST'])
def reconhecer():
    data_url = request.json['image']
    header, encoded = data_url.split(",", 1)
    img_bytes = b64decode(encoded)
    resultados = process_image(img_bytes)
    return jsonify(resultados)

# --- Logout ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# --- Rodar o app ---
if __name__ == "__main__":
    app.run(debug=True)