# Importando ferramentas necessárias
import os
import psycopg2
from flask import Flask, jsonify, request
from datetime import date, timedelta
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from passlib.hash import pbkdf2_sha256
from flask_cors import CORS
from urllib.parse import urlparse


# Começamos configurando a aplicação Flask e suas extensões
app = Flask(__name__) ##Criar uma instância do flask
# Define uma chave secreta para a segurança dos tokens JWT (JSON Web Tokens)
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY', 'chave-secreta-padrao')
# Habilita o CORS para permitir que o frontend (rodando em outro lugar) possa conversar com esta API
CORS(app)
# Inicia o gerenciador de tokens JWT
jwt = JWTManager(app)
# Pega a data de hoje para usar nas reservas
hoje = date.today()

# Função para conectar com o banco de dados
def get_db_connection():
    ## Coletando URL do Banco de Dados
    database_url = os.environ.get('DATABASE_URL')

    if database_url:
        # Parse da URL
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

# Rota padrão para testar conectividade
@app.route("/")
def home():
    return jsonify({"message": "Projeto ok"})

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
        # Inserimos o novo usuário no banco de dados de forma segura, usando '%s' para evitar ataques de SQL Injection
        cursor.execute("INSERT INTO USUARIOS (NOME, GENERO, IDADE, EMAIL, SENHA) VALUES (%s,%s,%s,%s,%s)", (username, genero, idade, email, senha_hash))
        conexao.commit()
        # Após cadastrar, já buscamos os dados do novo usuário para fazer o login
        cursor.execute("SELECT ID, NOME FROM USUARIOS WHERE EMAIL = %s", (email,))
        user = cursor.fetchone()
        user_id, username = user
        # Criamos um token de acesso para que ele não precise logar de novo
        token = create_access_token(identity=str(user_id))
        return jsonify({"message": "Usuário cadastrado com sucesso!", "token": token, "username": username}), 200

    # Retorna erro de integridade porque a coluna email só aceita valores únicos
    except psycopg2.IntegrityError:
        # Isso acontece se o email já existir no banco de dados
        return jsonify({"message": "Já existe um usuário com este e-mail"}), 400

    ##Fechamento do banco de dados
    finally:
        conexao.close()

    pass

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
    cursor.execute("SELECT livros.*, reservas.id AS id_reserva, CASE WHEN reservas.id_usuario = %s THEN TRUE "
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

    pass

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
                   "%s", (id_usuario,))

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

    pass

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
    cursor.execute("SELECT QTD_RESERVAS FROM USUARIOS WHERE ID = %s", (id_usuario,))
    qtd_reservas = cursor.fetchone()[0]

    if qtd_reservas != None:
        conexao.close()
        return jsonify({"message": "Não é possível fazer mais de uma reserva ao mesmo tempo"}), 400

    # Depois, garantimos que o livro escolhido está realmente disponível
    cursor.execute("SELECT disponibilidade FROM livros WHERE id = %s", (id_livro,))
    disponibilidade = cursor.fetchone()[0]
    if disponibilidade == True:
        # Se tudo estiver certo, criamos a reserva no banco de dados
        cursor.execute("INSERT INTO reservas (id_usuario, id_livro, data_reserva, data_devolucao) VALUES (%s, %s, %s, %s)", (id_usuario, id_livro, hoje, hoje + timedelta(days=30)))
        # E atualizamos o status do livro e do usuário
        cursor.execute("UPDATE livros SET disponibilidade = FALSE WHERE ID = %s", (id_livro,))
        cursor.execute("UPDATE USUARIOS SET QTD_RESERVAS = 1 WHERE ID = %s", (id_usuario,))
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
    cursor.execute("SELECT data_devolucao_real FROM reservas WHERE ID = %s", (id_reserva,))
    devolution_date = cursor.fetchone()[0]

    if devolution_date is not None:
        return jsonify({"message": "Este livro já foi devolvido nesta reserva"}), 400

    # Consultar o proprietário da reserva informada
    cursor.execute("SELECT id_usuario FROM reservas WHERE id = %s", (id_reserva,))
    book_owner = cursor.fetchone()[0]

    if book_owner is not None:
        book_owner = str(book_owner)
        # Testar se o proprietário da reserva informada é diferente do usuário logado
        if book_owner != id_usuario:
            conexao.close()
            return jsonify({"message": "Não é você quem está em posse deste livro."}), 400
        else:
            # Em caso de igualdade, realizar a devolução do livro
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



