import sqlite3

##Criação do banco de dados
conexao = sqlite3.connect("kaue.db")

##Cursor para executar comandos sql
cursor = conexao.cursor()

#Cria as seguintes tabelas: Usuarios, Livros, Reservas e Avaliações

#Salva e fecha a conexão
conexao.commit()
conexao.close()