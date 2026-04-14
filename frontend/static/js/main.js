/**
 * main.js — utilitários globais
 *
 * Funções partilhadas por todas as páginas:
 * - gestão do token JWT
 * - fetch autenticado
 */

const Auth = {
    getToken() {
        return localStorage.getItem("access_token");
    },

    setToken(token) {
        localStorage.setItem("access_token", token);
    },

    clearToken() {
        localStorage.removeItem("access_token");
    },

    isLoggedIn() {
        return !!this.getToken();
    },
};

/**
 * Wrapper sobre fetch que injeta automaticamente o Bearer token.
 * Uso: await apiFetch("/compliance/", { method: "GET" })
 */
async function apiFetch(url, options = {}) {
    const token = Auth.getToken();
    const headers = {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(options.headers || {}),
    };

    const res = await fetch(url, { ...options, headers });

    if (res.status === 401) {
        // Token expirado ou inválido — redirecionar para login
        Auth.clearToken();
        window.location.href = "/auth/login";
        return;
    }

    return res;
}
