from flask import Flask, render_template, request, redirect, flash
import psycopg2
import requests
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configuração do banco de dados
DATABASE_URL = os.getenv("POSTGRES_URL")

# Configuração do Vercel Blob
BLOB_API_URL = "https://vercel.blob/api/v1"
BLOB_READ_WRITE_TOKEN = os.getenv("BLOB_READ_WRITE_TOKEN")

def criar_conexao():
    try:
        conexao = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conexao
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

@app.route('/')
def index():
    return redirect('/index')

@app.route('/index', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        imagem = request.files['imagem']  # Receber o arquivo de imagem

        # Verificar se os campos estão preenchidos
        if not nome or not email or not senha:
            flash("Todos os campos são obrigatórios!", "error")
            return redirect('/index')

        # Fazer upload da imagem para o Blob da Vercel
        blob_url = upload_image_to_vercel(imagem)
        if not blob_url:
            flash("Erro ao enviar imagem.", "error")
            return redirect('/index')

        # Inserir no banco de dados
        conexao = criar_conexao()
        if conexao:
            try:
                cursor = conexao.cursor()
                query = """
                    INSERT INTO usuarios (nome, email, senha, imagem_url) 
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (nome, email, senha, blob_url))
                conexao.commit()
                flash("Usuário cadastrado com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao inserir no banco de dados: {e}", "error")
            finally:
                cursor.close()
                conexao.close()
        else:
            flash("Erro ao conectar ao banco de dados.", "error")
        return redirect('/index')

    return render_template('index.html')

def upload_image_to_vercel(imagem):
    """Faz o upload da imagem para o Blob da Vercel e retorna o URL."""
    try:
        headers = {"Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}"}
        files = {"file": (imagem.filename, imagem.stream, imagem.mimetype)}
        response = requests.post(f"{BLOB_API_URL}/upload", headers=headers, files=files)
        if response.status_code == 200:
            return response.json().get("url")  # Retorna o URL da imagem
        else:
            print("Erro no upload:", response.json())
            return None
    except Exception as e:
        print("Erro ao fazer upload para o Blob:", e)
        return None

if __name__ == '__main__':
    app.run(debug=True)
