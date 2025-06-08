import mysql.connector
from werkzeug.security import generate_password_hash

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vergil1@",
    database="ATP3"
)
cursor = conn.cursor()

senha_hash = generate_password_hash("senha123")
cursor.execute("""
INSERT INTO Professores (nome, email, senha)
VALUES (%s, %s, %s)
""", ("Professor Teste", "vish@gmail.com", senha_hash))

conn.commit()
cursor.close()
conn.close()
