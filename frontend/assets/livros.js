// Listar os livros
document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");
    const username = localStorage.getItem("username");
    const API_URL = "https://library-q1vj.onrender.com"; //Configurado com o domínio resultante do Deploy
    
    if (!token) {
        alert("Você precisa fazer login primeiro");
        window.location.href = "index.html"; // Redireciona
        return;
    }

    try {
        //Mostra o nome do usuário no cabeçalho
        document.getElementById("nomeUsuario").textContent = `Olá ${username}!`;
        //Mostrar estado de carregamento
        const livrosList = document.getElementById("livrosList");
        livrosList.innerHTML = "<p>Carregando livros...</p>";

        //Inicia conexão com o servidor na rota necessária
        const response = await fetch(`${API_URL}/listar_livros`, {
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            }
        });

        //Verificar erros HTTP
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || "Erro ao carregar livros");
        }

        //Processar os livros
        const livros = await response.json();
        console.log("Dados recebidos:", livros);

        if (livros.length === 0) {
            livrosList.innerHTML = "<p>Nenhum livro disponível.</p>";
            return;
        }

        //Mostrar os livros
        livrosList.innerHTML = livros.map(livro => `
            <div class="livro-card">
                <h3>${livro.titulo_livro}</h3>
                <p>Autor: ${livro.autor}</p>
                <p>ID Reserva: ${livro.id_reserva}</p>
                <p>Status: ${livro.disponibilidade ? "Disponível" : "Indisponível"}</p>
                ${!livro.disponibilidade && livro.usuario_reservou ?
                    `<button onclick="devolverLivro(${livro.id_reserva})">Devolver</button>` :
                    `<button onclick="reservarLivro(${livro.id})" ${livro.disponibilidade ? '' : 'disabled'}>
                    ${livro.disponibilidade ? 'Reservar' : 'Indisponível'}
                </button>`
                }
            </div>
        `).join("");

    } catch (error) {
        console.error("Erro:", error);
        document.getElementById("livrosList").innerHTML = `
            <p class="error">Erro ao carregar livros: ${error.message}</p>
        `;
    }
});

//Função para reservar o livro
async function reservarLivro(idLivro) {
    const token = localStorage.getItem("token");
    const API_URL = "https://library-q1vj.onrender.com"; //Configurado com o domínio resultante do Deploy
    
    try {
        //Inicia conexão com o servidor na rota necessária
        const response = await fetch(`${API_URL}/reservar`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ id_livro: idLivro })
        });

        const data = await response.json();
        alert(data.message);
        window.location.reload();
    } catch (error) {
        console.error("Erro:", error);
    }
}

//Função para devolver o livro
async function devolverLivro(idReserva) {
    const token = localStorage.getItem("token");
    const API_URL = "https://library-q1vj.onrender.com"; //Configurado com o domínio resultante do Deploy
    
    try {
        //Inicia conexão com o servidor na rota necessária
        const response = await fetch(`${API_URL}/devolver`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ id_reserva: idReserva })
        });

        const data = await response.json();
        alert(data.message);
        window.location.reload();
    } catch (error) {
        console.error("Erro:", error);
    }
}

async function logout() {
    localStorage.removeItem("token");
    
    window.location.href = "index.html"; // Redireciona
        
    alert("Logout realizado com sucesso!");
}

