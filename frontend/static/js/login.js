/**
 * login.js — lógica da página de autenticação
 *
 * Fluxo:
 *  1. Utilizador submete username + password → POST /auth/login
 *  2a. Se requires_2fa === true → mostrar campo TOTP
 *  2b. Se não → guardar token e redirecionar para dashboard
 *  3. Utilizador submete código TOTP → POST /auth/verify-2fa → token
 */

document.getElementById("form-login").addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorEl = document.getElementById("error-msg");
    errorEl.classList.add("hidden");

    const body = {
        username: document.getElementById("username").value.trim(),
        password: document.getElementById("password").value,
    };

    const res = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });

    const data = await res.json();

    if (!res.ok) {
        errorEl.textContent = data.detail || "Erro ao autenticar.";
        errorEl.classList.remove("hidden");
        return;
    }

    if (data.requires_2fa) {
        // Mostrar passo 2 — código TOTP
        document.getElementById("totp-username").value = body.username;
        document.getElementById("form-login").classList.add("hidden");
        document.getElementById("form-2fa").classList.remove("hidden");
        return;
    }

    // Login directo (sem 2FA)
    localStorage.setItem("access_token", data.access_token);
    window.location.href = "/";
});


document.getElementById("form-2fa").addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorEl = document.getElementById("error-2fa");
    errorEl.classList.add("hidden");

    const body = {
        username: document.getElementById("totp-username").value,
        code: document.getElementById("totp-code").value.trim(),
    };

    const res = await fetch("/auth/verify-2fa", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });

    const data = await res.json();

    if (!res.ok) {
        errorEl.textContent = data.detail || "Código inválido.";
        errorEl.classList.remove("hidden");
        return;
    }

    localStorage.setItem("access_token", data.access_token);
    window.location.href = "/";
});
