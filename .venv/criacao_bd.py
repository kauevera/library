import sqlite3

##Criação do banco de dados
conexao = sqlite3.connect("kaue.db")

##Cursor para executar comandos sql
cursor = conexao.cursor()

#Cria as seguintes tabelas: Usuarios, Livros, Reservas e Avaliações
cursor.executescript(""" 
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        genero TEXT NOT NULL,
        idade INTEGER
    );
    
    CREATE TABLE IF NOT EXISTS livros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo_livro TEXT NOT NULL,
        genero TEXT NOT NULL,
        autor TEXT NOT NULL,
        data_lancamento DATE,
        disponibilidade BOOLEAN
    );
    
    CREATE TABLE IF NOT EXISTS reservas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER,
        id_livro INTEGER,
        data_reserva DATE,
        data_devolucao DATE,
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
        FOREIGN KEY (id_livro) REFERENCES livros(id)    
    );
    
    CREATE TABLE IF NOT EXISTS avaliacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_livro INTEGER,
        id_usuario INTEGER,
        nota INTEGER,
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
        FOREIGN KEY (id_livro) REFERENCES livros(id)  
    )
    
    """)

#Salva e fecha a conexão
conexao.commit()
conexao.close()