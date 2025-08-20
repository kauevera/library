//Login
document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const senha = document.getElementById("senha").value;

    try {
        const response = await fetch("http://localhost:5000/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, senha })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("token", data.token); // Armazena o token
            localStorage.setItem("username", data.username); // Armazena o username
            alert(data.message || "O login deu certo!");
            window.location.href = "livros.html";
            //window.location.href = "livros.html"; // Redireciona
        } else {
            alert(data.message || "Erro no login");
        }
    } catch (error) {
        console.error("Erro:", error);
    }
});



