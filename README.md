# 📚 Biblioteca Online | CS50 Final Project

Este é um sistema de gestão de biblioteca desenvolvido como projeto final para o curso **CS50 da Harvard University**. A aplicação permite gerenciar o ciclo completo de empréstimos, desde o cadastro de utilizadores até ao controlo de disponibilidade de títulos.

## ✨ Funcionalidades

* **Autenticação Segura:** Registo e login utilizando tokens **JWT** e criptografia de palavras-passe.
* **Gestão de Acervo:** Visualização detalhada de livros disponíveis.
* **Reservas Inteligentes:** Sistema de reserva e devolução com controlo rigoroso de datas.
* **Painel do Utilizador:** Perfil dedicado para acompanhamento de empréstimos ativos.
* **Interface Adaptável:** Design totalmente responsivo para dispositivos móveis e desktop.

## 🛠️ Tecnologias

### **Backend**
* **Linguagem:** Python 3
* **Framework:** Flask
* **Banco de Dados:** PostgreSQL (Hospedado no Neon) / SQLite (Desenvolvimento)
* **Segurança:** JWT (JSON Web Tokens) e Passlib

### **Frontend**
* **Estrutura/Estilo:** HTML5 & CSS3
* **Lógica:** JavaScript (ES6+)
* **Comunicação:** Fetch API

## 🚀 Como Executar o Projeto

1.  **Clonar o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/library.git
    cd library
    ```

2.  **Criar ambiente Python:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instalar as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Iniciar o servidor:**
    ```bash
    python app.py
    ```
    A aplicação estará disponível em `http://localhost:5000`.

## 🗃️ Estrutura do Banco de Dados

O sistema utiliza uma arquitetura relacional com as seguintes tabelas principais:

* **`usuarios`**: Armazena dados de perfil e `senha_hash`.
* **`livros`**: Contém detalhes técnicos e a flag de `disponibilidade`.
* **`reservas`**: Tabela associativa que liga utilizadores a livros, registando datas de reserva e devolução.

## 👨‍💻 Autor
**Kauê Vera**
*Projeto Final - CS50 Introduction to Computer Science*