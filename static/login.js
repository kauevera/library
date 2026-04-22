//Login
document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const senha = document.getElementById("senha").value;
    const API_URL = "http://localhost:5000"; //Configurado com o domínio local

    try {
        //Inicia conexão com o servidor na rota necessária
        const response = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, senha })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("token", data.token); // Armazena o token
            localStorage.setItem("username", data.username); // Armazena o Username
            alert(data.message || "O login deu certo!");
            window.location.href = "/livros"; // Redireciona            
        } else {
            alert(data.message || "Erro no login");
        }
    } catch (error) {
        console.error("Erro:", error);
    }
});



