// Listar as reservas
document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");
    const username = localStorage.getItem("username");
    const API_URL = "https://library-backend-p7ql.onrender.com";
    
    if (!token) {
        alert("Você precisa fazer login primeiro");
        window.location.href = "index.html";
        return;
    }

    try {
        //Mostra o nome do usuário no cabeçalho
        document.getElementById("nomeUsuario").textContent = `Reservas de ${username}`;
        //Mostrar estado de carregamento
        const reservasList = document.getElementById("reservasList");
        reservasList.innerHTML = "<p>Carregando reservas...</p>";

        //Fazer a requisição com headers corretos
        const response = await fetch(`${API_URL}/listar_reservas`, {
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            }
        });

        //Verificar erros HTTP
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || "Erro ao carregar reservas");
        }

        //Processar as reservas
        const reservas = await response.json();
        console.log("Dados recebidos:", reservas); // Debug

        if (reservas.length === 0) {
            reservasList.innerHTML = "<p>Nenhuma reserva disponível.</p>";
            return;
        }

        //Mostrar os livros
        reservasList.innerHTML = reservas.map(reserva => `
            <div class="reserva-card">
                <h3>${reserva.titulo_livro}</h3>
                <p>Genero: ${reserva.genero}</p>
                <p>Proprietário: ${reserva.proprietario}</p>
                <p>Data de início: ${reserva.data_reserva}</p>
                <p>Data de fim previsto: ${reserva.data_devolucao}</p>
                <p>Data de fim real: ${reserva.data_devolucao_real}</p>
                <p>ID Reserva: ${reserva.id}</p>
                <p>Status: ${reserva.state}</p>
                ${reserva.state == "Em andamento" ?
                    `<button onclick="devolverLivro(${reserva.id})">Devolver</button>`:
                    ''
                }
            </div>
        `).join("");

    } catch (error) {
        console.error("Erro:", error);
        document.getElementById("reservasList").innerHTML = `
            <p class="error">Erro ao carregar reservas: ${error.message}</p>
        `;
    }
});

//Função para devolver o livro
async function devolverLivro(idReserva) {
    const token = localStorage.getItem("token");
    
    try {
        const response = await fetch("http://localhost:5000/devolver", {
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
    
    window.location.href = "index.html";
        
    alert("Logout realizado com sucesso!");
}
