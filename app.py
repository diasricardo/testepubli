from flask import Flask, render_template, request, redirect, flash
import psycopg2
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configuração do banco de dados
DATABASE_URL = os.getenv("POSTGRES_URL")

def criar_conexao():
    try:
        conexao = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conexao
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

@app.route('/')
def index():
    return redirect('/cadastro')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        # Verificar se os campos estão preenchidos
        if not nome or not email or not senha:
            flash("Todos os campos são obrigatórios!", "error")
            return redirect('/cadastro')

        # Inserir no banco de dados
        conexao = criar_conexao()
        if conexao:
            try:
                cursor = conexao.cursor()
                query = "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)"
                cursor.execute(query, (nome, email, senha))
                conexao.commit()
                flash("Usuário cadastrado com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao inserir no banco de dados: {e}", "error")
            finally:
                cursor.close()
                conexao.close()
        else:
            flash("Erro ao conectar ao banco de dados.", "error")
        return redirect('/cadastro')

    return render_template('cadastro.html')

if __name__ == '__main__':
    app.run(debug=True)
