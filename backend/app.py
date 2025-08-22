import os
import psycopg2
from flask import Flask, jsonify, request
from datetime import date, timedelta
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from passlib.hash import pbkdf2_sha256
from flask_cors import CORS
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

hoje = date.today()

app = Flask(__name__) ##Criar uma instância do flask
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY', 'chave-secreta-padrao')

CORS(app)

jwt = JWTManager(app)


def get_db_connection():
    # Se usar Neon.tech, eles fornecem uma URL completa
    database_url = os.environ.get('DATABASE_URL')

    if database_url:
        # Parse da URL do Neon
        parsed = urlparse(database_url)
        conn = psycopg2.connect(
            host=parsed.hostname,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password,
            port=parsed.port,
            sslmode='require'
        )
    else:
        # Fallback para variáveis individuais
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST'),
            database=os.environ.get('DB_NAME'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            port=os.environ.get('DB_PORT', 5432)
        )
    return conn

@app.route("/")
def home():
    return jsonify({"message": "Projeto ok"})

@app.route("/cadastrar", methods=['POST'])
def novo_usuario():
    data = request.json
    ##Coleta de dados do json
    username = data['nome']
    genero = data['genero']
    idade = data['idade']
    email = data.get('email')
    senha = data.get('senha')
    senha_hash = pbkdf2_sha256.hash(senha)

    ##Verifica se o email e a senha vieram no json
    if email == None or senha == None:
        return jsonify({"message": "É obrigatório informar o e-mail e a senha"}), 400

    ##Abertura do banco de dados
    conexao = get_db_connection()
    cursor = conexao.cursor()

    try:
        cursor.execute("INSERT INTO USUARIOS (NOME, GENERO, IDADE, EMAIL, SENHA) VALUES (%s,%s,%s,%s,%s)", (username, genero, idade, email, senha_hash))
        conexao.commit()
        cursor.execute("SELECT ID, NOME FROM USUARIOS WHERE EMAIL = %s", (email,))
        user = cursor.fetchone()
        user_id, username = user
        token = create_access_token(identity=str(user_id))
        return jsonify({"message": "Usuário cadastrado com sucesso!", "token": token, "username": username}), 200

    ##Retorna erro de integridade porque a coluna email só aceita valores únicos
    except psycopg2.IntegrityError:
        return jsonify({"message": "Já existe um usuário com este e-mail"}), 400

    ##Fechamento do banco de dados
    finally:
        conexao.close()

    pass

@app.route("/login", methods=['POST'])
def logar_usuario():
    data = request.json

    ##Coleta de dados do json
    email = data.get('email')
    senha = data.get('senha')

    ##Verifica se o email e a senha vieram no json
    if email == None or senha == None:
        return jsonify({"message": "É obrigatório informar o e-mail e a senha"}), 400

    ##Consultar o banco de dados
    conexao = get_db_connection()
    cursor = conexao.cursor()
    cursor.execute("SELECT ID, SENHA, NOME FROM USUARIOS WHERE EMAIL = %s", (email,))
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

    pass

@app.route("/listar_livros")
@jwt_required()
def lista_livros():
    id_usuario = get_jwt_identity()

    conexao = get_db_connection()
    cursor = conexao.cursor()

    #Consulta com LEFT JOIN para pegar o id reserva de livros indisponíveis
    cursor.execute("SELECT livros.*, reservas.id AS id_reserva, CASE WHEN reservas.id_usuario = %s THEN TRUE "
                   "ELSE FALSE END AS usuario_reservou FROM livros LEFT JOIN reservas "
                   "ON livros.id = reservas.id_livro AND livros.disponibilidade = FALSE "
                   "AND reservas.data_devolucao_real IS NULL", (id_usuario,))

    tabela_livros = cursor.fetchall()
    conexao.close()

    #Criar lista para armazenar os valores da consulta
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

    return jsonify(lista_livros)

    pass

@app.route("/listar_reservas")
@jwt_required()
def lista_reservas():
    id_usuario = get_jwt_identity()

    conexao = get_db_connection()
    cursor = conexao.cursor()

    #Consulta com LEFT JOIN para pegar o id reserva de livros indisponíveis
    cursor.execute("SELECT reservas.id, reservas.data_reserva, reservas.data_devolucao, reservas.data_devolucao_real, "
                   "USUARIOS.NOME AS proprietario, livros.titulo_livro, livros.genero, CASE WHEN reservas.data_devolucao_real IS NULL THEN "
                   "'Em andamento' ELSE 'Ja devolvido' END AS state FROM reservas LEFT JOIN USUARIOS ON USUARIOS.ID = "
                   "reservas.id_usuario LEFT JOIN livros ON livros.id = reservas.id_livro WHERE reservas.id_usuario = "
                   "%s", (id_usuario,))

    tabela_reservas = cursor.fetchall()
    conexao.close()

    #Criar lista para armazenar os valores da consulta
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

    return jsonify(lista_reservas)

    pass

@app.route("/reservar", methods=['POST'])
@jwt_required()
def reservar_livro():
    data = request.json
    ##Coletar o ID que irá ao banco de dados
    id_livro = data['id_livro']
    id_usuario = get_jwt_identity()

    conexao = get_db_connection()
    cursor = conexao.cursor()

    ##Consultar se o usuário já tem uma reserva
    cursor.execute("SELECT QTD_RESERVAS FROM USUARIOS WHERE ID = %s", (id_usuario,))
    qtd_reservas = cursor.fetchone()[0]

    if qtd_reservas != None:
        conexao.close()
        return jsonify({"message": "Não é possível fazer mais de uma reserva ao mesmo tempo"}), 400

    ##Consultar disponibilidade do livro na tabela livros
    cursor.execute("SELECT disponibilidade FROM livros WHERE id = %s", (id_livro,))
    disponibilidade = cursor.fetchone()[0]
    if disponibilidade == False:
        cursor.execute("INSERT INTO reservas (id_usuario, id_livro, data_reserva, data_devolucao) VALUES (%s, %s, %s, %s)", (id_usuario, id_livro, hoje, hoje + timedelta(days=30)))
        cursor.execute("UPDATE livros SET disponibilidade = FALSE WHERE ID = %s", (id_livro,))
        cursor.execute("UPDATE USUARIOS SET QTD_RESERVAS = 1 WHERE ID = %s", (id_usuario,))
        conexao.commit()
        conexao.close()
        return jsonify({"message": "Seu livro foi reservado com sucesso!"}), 200
        ##Retornar mensagem explicativa caso o livro não esteja disponível
    else:
        conexao.close()
        return jsonify({"message": "Este livro está indisponível no momento."}), 400
@app.route("/devolver", methods=['POST'])
@jwt_required()
def devolver_livro():
    data = request.json
    ##Coletar o ID que irá ao banco de dados
    id_reserva = data['id_reserva']
    id_usuario = get_jwt_identity()

    conexao = get_db_connection()
    cursor = conexao.cursor()

    ##Consultar se a reserva está em andamento
    cursor.execute("SELECT data_devolucao_real FROM reservas WHERE ID = %s", (id_reserva,))
    devolution_date = cursor.fetchone()[0]

    if devolution_date is not None:
        return jsonify({"message": "Este livro já foi devolvido nesta reserva"}), 400

    ##Consultar se o proprietário da reserva recebida é igual ao usuário que está solicitando a devolução
    cursor.execute("SELECT id_usuario FROM reservas WHERE id = %s", (id_reserva,))
    book_owner = cursor.fetchone()[0]

    if book_owner is not None:
        book_owner = str(book_owner)
        if book_owner != id_usuario:
            conexao.close()
            return jsonify({"message": "Não é você quem está em posse deste livro."}), 400
        else:
            cursor.execute("SELECT id_livro FROM reservas WHERE id = %s", (id_reserva,))
            id_livro = cursor.fetchone()[0]
            cursor.execute("UPDATE livros SET disponibilidade = TRUE WHERE id = %s", (id_livro,))
            cursor.execute("UPDATE USUARIOS SET QTD_RESERVAS = NULL WHERE ID = %s", (id_usuario,))
            cursor.execute("UPDATE reservas SET data_devolucao_real = %s WHERE id = %s", (hoje, id_reserva))
            conexao.commit()
            conexao.close()
            return jsonify({"message": "Livro devolvido com sucesso!"}), 200

    else:
        return jsonify({"message": "Esse livro não foi reservado ainda"}), 400

    pass

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)



