import sqlite3
import pandas

conexao = sqlite3.connect("kaue.db")
cursor = conexao.cursor()

usuarios = pandas.read_sql_query("SELECT * FROM USUARIOS", conexao)
livros = pandas.read_sql_query("SELECT * FROM LIVROS", conexao)
reservas = pandas.read_sql_query("SELECT * FROM RESERVAS", conexao)
avaliacoes = pandas.read_sql_query("SELECT * FROM AVALIACOES", conexao)

print(usuarios)
print(livros)
print(reservas)
print(avaliacoes)







