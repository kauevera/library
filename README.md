📚 Biblioteca Online
🎓 Sobre o Projeto
Um sistema completo de biblioteca online desenvolvido como projeto final para o curso CS50 da Harvard. O sistema permite que usuários se cadastrem, façam login, visualizem livros disponíveis e realizem reservas de forma intuitiva e segura.

✨ Funcionalidades Principais
🔐 Sistema de Autenticação JWT - Cadastro e login seguro de usuários
📖 Catálogo de Livros - Listagem completa do acervo disponível
🔄 Sistema de Reservas - Reserva e devolução de livros com controle de datas
👤 Perfil de Usuário - Acompanhamento de reservas em andamento
🎨 Interface Responsiva - Design adaptável para desktop e mobile

🛠️ Tecnologias Utilizadas
Backend
Python 3 - Linguagem principal
Flask - Framework web
Postgre - Banco de dados no Neon
JWT - Autenticação segura
Passlib - Criptografia de senhas

Frontend
HTML5 - Estrutura semântica
CSS3 - Estilização moderna
JavaScript ES6+ - Interatividade
Fetch API - Comunicação com backend

⁉️ Como testar o projeto
Instalação e Execução
# Clone o repositório
git clone library
cd library

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python app.py

🔌 API Endpoints
Autenticação
POST /api/cadastrar - Registrar novo usuário
POST /api/login - Fazer login na aplicação
******************************************************************************
Livros
GET /api/listar_livros - Listar todos os livros (requer autenticação)
POST /api/reservar - Reservar livro (requer autenticação)
POST /api/devolver - Devolver livro (requer autenticação)
******************************************************************************
Usuário
GET /api/listar_reservas - Listar reservas do usuário (requer autenticação)

🗃️ Estrutura do Banco de Dados
O sistema utiliza SQLite com as seguintes tabelas:

🔡Tabela usuarios
id INTEGER PRIMARY KEY AUTOINCREMENT
nome TEXT NOT NULL
email TEXT UNIQUE NOT NULL
senha_hash TEXT NOT NULL
genero TEXT
idade INTEGER
qtd_reservas INTEGER
******************************************************************************
🔡Tabela livros
sql
id INTEGER PRIMARY KEY AUTOINCREMENT
titulo_livro TEXT NOT NULL
autor TEXT NOT NULL
genero TEXT
data_lancamento TEXT
disponibilidade BOOLEAN
******************************************************************************
🔡Tabela reservas
sql
id INTEGER PRIMARY KEY AUTOINCREMENT
id_usuario INTEGER FOREIGN KEY
id_livro INTEGER FOREIGN KEY
data_reserva TEXT
data_devolucao TEXT
data_devolucao_real TEXT

👨💻 Autor
Kauê Vera - Desenvolvido como projeto final do CS50