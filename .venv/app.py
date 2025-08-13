import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__) ##Criar uma instância do flask

@app.route("/listar")
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

    conexao = sqlite3.connect("kaue.db")
    cursor = conexao.cursor()

    ##Consultar disponibilidade no banco de dados
    cursor.execute("SELECT DISPONIBILIDADE FROM LIVROS WHERE id = ?", (id_livro,))
    disponibilidade = cursor.fetchone()[0]

    ##Atualizando o status do livro se ele estiver disponvel
    if disponibilidade == 1:
        cursor.execute("UPDATE LIVROS SET DISPONIBILIDADE = 0 WHERE id = ?", (id_livro,))
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

if __name__ == '__main__':
    app.run(debug=True)