import sqlite3
from flask import Flask, jsonify, request
from datetime import date, timedelta
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from passlib.hash import pbkdf2_sha256

hoje = date.today()

app = Flask(__name__) ##Criar uma instância do flask
app.config["JWT_SECRET_KEY"] = "S@ntos20,02" ##Chave secreta para autenticação
jwt = JWTManager(app)

@app.route("/cadastrar", methods=['POST'])
def novo_usuario():
    data = request.json
    ##Coleta de dados do json
    username = data['nome']
    genero = data['genero']
    idade = data['idade']
    email = data.get['email']
    senha = data.get['senha']
    senha_hash = pbkdf2_sha256.hash(senha)

    ##Verifica se o email e a senha vieram no json
    if email == None or senha == None:
        return jsonify({"message": "É obrigatório informar o e-mail e a senha"}), 400

    ##Abertura do banco de dados
    conexao = sqlite3.connect("kaue.db")
    cursor = conexao.cursor()

    try:
        cursor.execute("INSERT INTO USUARIOS (NOME, GENERO, IDADE, EMAIL, SENHA) VALUES (?,?,?,?,?)", (username, genero, idade, email, senha_hash))
        conexao.commit()
        return jsonify({"message": "Usuário cadastrado com sucesso!"}), 200

    ##Retorna erro de integridade porque a coluna email só aceita valores únicos
    except sqlite3.IntegrityError:
        return jsonify({"message": "Já existe um usuário com este e-mail"}), 400

    ##Fechamento do banco de dados
    finally:
        conexao.close()


@app.route("/login", methods=['POST'])
def logar_usuario():
    data = request.json

    ##Coleta de dados do json
    email = data.get['email']
    senha = data.get['senha']

    ##Verifica se o email e a senha vieram no json
    if email == None or senha == None:
        return jsonify({"message": "É obrigatório informar o e-mail e a senha"}), 400

    ##Consultar o banco de dados
    conexao = sqlite3.connect("kaue.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT ID, SENHA FROM USUARIOS WHERE EMAIL = ?", (email,))
    user = cursor.fetchone()
    conexao.close()

    ##Retorna None se o campo de senha estiver vazio ou incorreto no banco
    if user == None:
        return jsonify({"message": "O usuário ou a senha estão incorretos."}), 400

    user_id, hash_senha = user

    ##Testa se o hash que veio do banco de dados, quando convertido para senha, é igual à senha digitada pelo usuário
    if pbkdf2_sha256.verify(senha, hash_senha) == False:
        return jsonify({"message": "O usuário ou a senha estão incorretos."}), 400

    token = create_access_token(identity=user_id)
    return jsonify({"token": token}), 200

@app.route("/listar_livros")
def lista_livros():
    ##Consultar o banco de dados
    conexao = sqlite3.connect("kaue.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM LIVROS")
    tabela_livros = cursor.fetchall()
    conexao.close()

    ##Transformar a consulta do banco de dados em uma lista do Python
    lista_livros = []
    for livro in tabela_livros:
        lista_livros.append({
            'id': livro[0],
            'titulo_livro': livro[1],
            'genero': livro[2],
            'autor': livro[3],
            'data_lancamento': livro[4],
            'disponibilidade': bool(livro[5]),
        })

    ##Retornar a lista como um arquivo JSON
    return jsonify(lista_livros)

@app.route("/reservar", methods=['POST'])
def reservar_livro():
    data = request.json
    ##Coletar o ID que irá ao banco de dados
    id_livro = data['id_livro']
    id_usuario = data['id_usuario']

    conexao = sqlite3.connect("kaue.db")
    cursor = conexao.cursor()

    ##Consultar existencia do usuario na tabela usuarios
    cursor.execute("SELECT ID FROM USUARIOS WHERE id = ?", (id_usuario,))
    existencia = cursor.fetchone()
    if existencia == None:
        conexao.close()
        return jsonify({"message": "Usuario com o ID informado não foi encontrado."}), 404

    ##Consultar existencia do livro na tabela livros
    cursor.execute("SELECT ID FROM LIVROS WHERE id = ?", (id_livro,))
    existencia = cursor.fetchone()
    if existencia == None:
        conexao.close()
        return jsonify({"message": "Livro com o ID informado não foi encontrado."}), 404

    ##Consultar disponibilidade do livro na tabela livros
    cursor.execute("SELECT DISPONIBILIDADE FROM LIVROS WHERE id = ?", (id_livro,))
    disponibilidade = cursor.fetchone()[0]
    if disponibilidade == 1:
        cursor.execute("INSERT INTO RESERVAS (id_usuario, id_livro, data_reserva, data_devolucao) VALUES (?, ?, ?, ?)", (id_usuario, id_livro, hoje, hoje + timedelta(days=30)))
        cursor.execute("UPDATE LIVROS SET DISPONIBILIDADE = 0 WHERE ID = ?", (id_livro,))
        conexao.commit()
        conexao.close()
        return jsonify({"message": "Seu livro foi reservado com sucesso!"}), 200
        ##Retornar mensagem explicativa caso o livro não esteja disponível
    else:
        conexao.close()
        return jsonify({"message": "Este livro está indisponível no momento."}), 400
@app.route("/devolver", methods=['POST'])
def devolver_livro():
    data = request.json
    ##Coletar o ID que irá ao banco de dados
    id_livro = data['id_livro']

    conexao = sqlite3.connect("kaue.db")
    cursor = conexao.cursor()

    ##Consultar disponibilidade no banco de dados
    cursor.execute("SELECT DISPONIBILIDADE FROM LIVROS WHERE id = ?", (id_livro,))
    disponibilidade = cursor.fetchone()[0]

    ##Atualizando o status do livro se ele estiver mesmo emprestado
    if disponibilidade == 0:
        cursor.execute("UPDATE LIVROS SET DISPONIBILIDADE = 1 WHERE id = ?", (id_livro,))
        conexao.commit()
        conexao.close()
        return jsonify({"message": "Livro devolvido com sucesso!"}), 200
    ##Retornar mensagem explicativa caso o livro não precise ser devolvido
    else:
        conexao.close()
        return jsonify({"message": "Este livro não precisa ser devolvido."}), 400


@app.route("/avaliar", methods=['POST'])
def avaliar_livro():
    data = request.json

    conexao = sqlite3.connect("kaue.db")
    cursor = conexao.cursor()

    ##Coletar o ID do livro e pessoa que irá ao banco de dados
    id_livro = data['id_livro']
    id_pessoa = data['id_pessoa']
    nota = data['nota']

    ##Consultar se existe uma avaliação com o livro e a pessoa informada
    cursor.execute("SELECT ID FROM AVALIACOES WHERE ID_USUARIO = ? AND ID_LIVRO = ?", (id_pessoa, id_livro,))
    id_avaliacoes = cursor.fetchone()[0]

    if (id_avaliacoes == NULL):
        conexao.close()
        return jsonify({"message": "Não é possível adicionar duas avaliações para o mesmo livro - Caso queira, é possível editar"}), 400

    else:
        cursor.execute("INSERT INTO AVALIACOES (id_livro, id_usuario, nota) VALUES (?, ?, ?)", (id_livro, id_pessoa, nota))
        conexao.commit()
        conexao.close()
        return jsonify({"message": "Sua avaliação foi enviada!"}), 200

if __name__ == '__main__':
    app.run(debug=True)