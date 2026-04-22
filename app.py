# Importando ferramentas necessárias
import sqlite3
from flask import Flask, jsonify, request, render_template
from datetime import date, timedelta
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from passlib.hash import pbkdf2_sha256
from flask_cors import CORS

# Começamos configurando a aplicação Flask e suas extensões
app = Flask(__name__) ##Criar uma instância do flask
# Define uma chave secreta para a segurança dos tokens JWT (JSON Web Tokens)
app.config["JWT_SECRET_KEY"] = "chave-secreta-padrao"
# Habilita o CORS para permitir que o frontend (rodando em outro lugar) possa conversar com esta API
CORS(app)
# Inicia o gerenciador de tokens JWT
jwt = JWTManager(app)
# Pega a data de hoje para usar nas reservas
hoje = date.today()

# Função para conectar com o banco de dados
def get_db_connection():
    conn = sqlite3.connect('biblioteca.db')
    # A linha abaixo faz com que os resultados do banco venham como dicionários,
    # o que torna o acesso aos dados mais fácil e intuitivo (ex: linha['coluna'])
    conn.row_factory = sqlite3.Row
    return conn

# Função para criar as tabelas do nosso banco de dados, caso ainda não existam
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Cria a tabela 'usuarios' para guardar os dados de quem usa o sistema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            genero TEXT,
            idade INTEGER,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            qtd_reservas INTEGER DEFAULT NULL
        )
    """)

    # Cria a tabela 'livros'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo_livro TEXT NOT NULL,
            genero TEXT,
            autor TEXT,
            data_lancamento TEXT,
            disponibilidade BOOLEAN DEFAULT TRUE
        )
    """)

    # Cria a tabela 'reservas' para controlar os empréstimos de livros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER,
            id_livro INTEGER,
            data_reserva TEXT,
            data_devolucao TEXT,
            data_devolucao_real TEXT DEFAULT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuarios (id),
            FOREIGN KEY (id_livro) REFERENCES livros (id)
        )
    """)

    # Criação de dados para testes
    cursor.execute("SELECT COUNT(*) FROM livros")
    if cursor.fetchone()[0] == 0:
        livros_exemplo = [
            ("Dom Quixote", "Romance", "Miguel de Cervantes", "1605-01-01", True),
            ("1984", "Ficção Científica", "George Orwell", "1949-06-08", True),
            ("Orgulho e Preconceito", "Romance", "Jane Austen", "1813-01-28", True),
            ("O Pequeno Príncipe", "Fábula", "Antoine de Saint-Exupéry", "1943-04-06", True)
        ]
        cursor.executemany(
            "INSERT INTO livros (titulo_livro, genero, autor, data_lancamento, disponibilidade) VALUES (?, ?, ?, ?, ?)",
            livros_exemplo
        )

    conn.commit()
    conn.close()

# Executa a função para garantir que o banco de dados e as tabelas estejam prontos
init_db()

# Rota padrão para testar conectividade
@app.route("/api")
def home():
    return jsonify({"message": "Projeto ok"})

# Rota principal que serve a página inicial (o arquivo index.html)
@app.route("/")
def index():
    return render_template("index.html")

# Rota para a página de cadastro
@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

# Rota para a página de livros
@app.route("/livros")
def livros():
    return render_template("livros.html")

# Rota para a página de reservas
@app.route("/reservas")
def reservas():
    return render_template("reservas.html")

# Rota para cadastrar um novo usuário
@app.route("/cadastrar", methods=['POST'])
def novo_usuario():
    data = request.json
    ##Coleta de dados do json
    username = data['nome']
    genero = data['genero']
    idade = data['idade']
    email = data.get('email')
    senha = data.get('senha')
    senha_hash = pbkdf2_sha256.hash(senha) ##Salvando o hash da senha - Nunca salvar o original

    # Verifica se o email e a senha vieram no json
    if email == None or senha == None:
        return jsonify({"message": "É obrigatório informar o e-mail e a senha"}), 400

    # Abertura do banco de dados
    conexao = get_db_connection()
    cursor = conexao.cursor()

    try:
        # Inserimos o novo usuário no banco de dados de forma segura, usando '?' para evitar ataques de SQL Injection
        cursor.execute("INSERT INTO USUARIOS (NOME, GENERO, IDADE, EMAIL, SENHA_HASH) VALUES (?,?,?,?,?)", (username, genero, idade, email, senha_hash))
        conexao.commit()
        # Após cadastrar, já buscamos os dados do novo usuário para fazer o login
        cursor.execute("SELECT ID, NOME FROM USUARIOS WHERE EMAIL = ?", (email,))
        user = cursor.fetchone()
        user_id, username = user
        # Criamos um token de acesso para que ele não precise logar de novo
        token = create_access_token(identity=str(user_id))
        return jsonify({"message": "Usuário cadastrado com sucesso!", "token": token, "username": username}), 200

    # Retorna erro de integridade porque a coluna email só aceita valores únicos
    except sqlite3.IntegrityError:
        # Isso acontece se o email já existir no banco de dados
        return jsonify({"message": "Já existe um usuário com este e-mail"}), 400

    ##Fechamento do banco de dados
    finally:
        conexao.close()

# Rota para fazer o login
@app.route("/login", methods=['POST'])
def logar_usuario():
    data = request.json

    # Coleta de dados do json
    email = data.get('email')
    senha = data.get('senha')

    # Verifica se o email e a senha vieram no json
    if email == None or senha == None:
        return jsonify({"message": "É obrigatório informar o e-mail e a senha"}), 400

    # Buscamos o usuário pelo email fornecido
    conexao = get_db_connection()
    cursor = conexao.cursor()
    cursor.execute("SELECT ID, SENHA_HASH, NOME FROM USUARIOS WHERE EMAIL = ?", (email,))
    user = cursor.fetchone()
    conexao.close()

    ##Retorna None se o campo de senha estiver vazio ou incorreto no banco
    if user == None:
        return jsonify({"message": "O usuário ou a senha estão incorretos."}), 400

    user_id, hash_senha, username = user

    ##Testa se o hash que veio do banco de dados, quando convertido para senha, é igual à senha digitada pelo usuário
    if pbkdf2_sha256.verify(senha, hash_senha) == False:
        return jsonify({"message": "O usuário ou a senha estão incorretos."}), 400

    token = create_access_token(identity=str(user_id))
    return jsonify({"token": token, "username": username}), 200

# Rota para listar os livros disponíveis
@app.route("/listar_livros")
@jwt_required()
def lista_livros():
    # Pegamos o ID do usuário que está logado, através do token
    id_usuario = get_jwt_identity()

    conexao = get_db_connection()
    cursor = conexao.cursor()

    # Esta consulta busca todos os livros e adiciona uma informação extra:
    # um campo 'usuario_reservou' que nos diz se o livro está reservado
    # pelo próprio usuário que fez a requisição.
    cursor.execute("SELECT livros.*, reservas.id AS id_reserva, CASE WHEN reservas.id_usuario = ? THEN TRUE "
                   "ELSE FALSE END AS usuario_reservou FROM livros LEFT JOIN reservas "
                   "ON livros.id = reservas.id_livro AND livros.disponibilidade = FALSE "
                   "AND reservas.data_devolucao_real IS NULL", (id_usuario,))

    tabela_livros = cursor.fetchall()
    conexao.close()

    # Criar lista para armazenar os valores da consulta
    lista_livros = []
    for livro in tabela_livros:
        lista_livros.append({
            'id': livro[0],
            'titulo_livro': livro[1],
            'genero': livro[2],
            'autor': livro[3],
            'data_lancamento': livro[4],
            'disponibilidade': bool(livro[5]),
            'id_reserva': livro[6],
            'usuario_reservou': livro[7]
        })

    # Envia os valores no JSON
    return jsonify(lista_livros)

# Rota para listar as reservas do usuário
@app.route("/listar_reservas")
@jwt_required()
def lista_reservas():
    # Pegamos o ID do usuário que está logado, através do token
    id_usuario = get_jwt_identity()

    conexao = get_db_connection()
    cursor = conexao.cursor()

    # Consulta com LEFT JOIN para pegar o id reserva de livros indisponíveis
    cursor.execute("SELECT reservas.id, reservas.data_reserva, reservas.data_devolucao, reservas.data_devolucao_real, "
                   "USUARIOS.NOME AS proprietario, livros.titulo_livro, livros.genero, CASE WHEN reservas.data_devolucao_real IS NULL THEN "
                   "'Em andamento' ELSE 'Ja devolvido' END AS state FROM reservas LEFT JOIN USUARIOS ON USUARIOS.ID = "
                   "reservas.id_usuario LEFT JOIN livros ON livros.id = reservas.id_livro WHERE reservas.id_usuario = "
                   "?", (id_usuario,))

    tabela_reservas = cursor.fetchall()
    conexao.close()

    # Criar lista para armazenar os valores da consulta
    lista_reservas = []
    for reserva in tabela_reservas:
        lista_reservas.append({
            'id': reserva[0],
            'data_reserva': reserva[1],
            'data_devolucao': reserva[2],
            'data_devolucao_real': reserva[3],
            'proprietario': reserva[4],
            'titulo_livro': reserva[5],
            'genero': reserva[6],
            'state': reserva[7]
        })

    # Envia os valores no JSON
    return jsonify(lista_reservas)

# Rota para reservar um livro
@app.route("/reservar", methods=['POST'])
@jwt_required()
def reservar_livro():
    data = request.json
    id_livro = data['id_livro'] #Coleta o ID do livro passado pela function
    id_usuario = get_jwt_identity() # Pegamos o ID do usuário que está logado, através do token

    conexao = get_db_connection()
    cursor = conexao.cursor()

    # Consultar se o usuário já tem uma reserva
    cursor.execute("SELECT QTD_RESERVAS FROM USUARIOS WHERE ID = ?", (id_usuario,))
    qtd_reservas = cursor.fetchone()[0]

    if qtd_reservas != None:
        conexao.close()
        return jsonify({"message": "Não é possível fazer mais de uma reserva ao mesmo tempo"}), 400

    # Depois, garantimos que o livro escolhido está realmente disponível
    cursor.execute("SELECT disponibilidade FROM livros WHERE id = ?", (id_livro,))
    disponibilidade = cursor.fetchone()[0]
    if disponibilidade == True:
        # Se tudo estiver certo, criamos a reserva no banco de dados
        cursor.execute("INSERT INTO reservas (id_usuario, id_livro, data_reserva, data_devolucao) VALUES (?, ?, ?, ?)", (id_usuario, id_livro, hoje, hoje + timedelta(days=30)))
        # E atualizamos o status do livro e do usuário
        cursor.execute("UPDATE livros SET disponibilidade = FALSE WHERE ID = ?", (id_livro,))
        cursor.execute("UPDATE USUARIOS SET QTD_RESERVAS = 1 WHERE ID = ?", (id_usuario,))
        conexao.commit()
        conexao.close()
        return jsonify({"message": "Seu livro foi reservado com sucesso!"}), 200

    else:
        conexao.close()
        ##Retornar mensagem explicativa caso o livro não esteja disponível
        return jsonify({"message": "Este livro está indisponível no momento."}), 400

# Rota para devolver um livro
@app.route("/devolver", methods=['POST'])
@jwt_required()
def devolver_livro():
    data = request.json
    id_reserva = data['id_reserva'] # Coleta o ID da reserva passada pela function
    id_usuario = get_jwt_identity() # Pegamos o ID do usuário que está logado, através do token

    conexao = get_db_connection()
    cursor = conexao.cursor()

    # Consultar se a reserva está em andamento
    cursor.execute("SELECT data_devolucao_real FROM reservas WHERE ID = ?", (id_reserva,))
    devolution_date = cursor.fetchone()[0]

    if devolution_date is not None:
        return jsonify({"message": "Este livro já foi devolvido nesta reserva"}), 400

    # Consultar o proprietário da reserva informada
    cursor.execute("SELECT id_usuario FROM reservas WHERE id = ?", (id_reserva,))
    book_owner = cursor.fetchone()[0]

    if book_owner is not None:
        book_owner = str(book_owner)
        # Testar se o proprietário da reserva informada é diferente do usuário logado
        if book_owner != id_usuario:
            conexao.close()
            return jsonify({"message": "Não é você quem está em posse deste livro."}), 400
        else:
            # Em caso de igualdade, realizar a devolução do livro
            cursor.execute("SELECT id_livro FROM reservas WHERE id = ?", (id_reserva,))
            id_livro = cursor.fetchone()[0]
            cursor.execute("UPDATE livros SET disponibilidade = TRUE WHERE id = ?", (id_livro,))
            cursor.execute("UPDATE USUARIOS SET QTD_RESERVAS = NULL WHERE ID = ?", (id_usuario,))
            cursor.execute("UPDATE reservas SET data_devolucao_real = ? WHERE id = ?", (hoje, id_reserva))
            conexao.commit()
            conexao.close()
            return jsonify({"message": "Livro devolvido com sucesso!"}), 200

    else:
        return jsonify({"message": "Esse livro não foi reservado ainda"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)



