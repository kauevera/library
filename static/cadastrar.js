//Cadastrar
document.getElementById("signInForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const nome = document.getElementById("username").value;
    const genero = document.querySelector('input[name="gender"]:checked').value;
    const idade = document.getElementById("age").value;
    const email = document.getElementById("email").value;
    const senha = document.getElementById("senha").value;
    const API_URL = "http://localhost:5000"; //Configurado com o domínio local

    try {
        //Inicia conexão com o servidor na rota necessária
        const response = await fetch(`${API_URL}/cadastrar`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nome, genero, idade, email, senha })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("token", data.token); // Armazena o token
            localStorage.setItem("username", data.username); // Armazena o username
            alert(data.message);
            window.location.href = "/livros"; // Redireciona
        } else {
            alert(data.message || "Erro no cadastro");
        }
    } catch (error) {
        console.error("Erro:", error);
    }
});