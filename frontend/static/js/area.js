/**
 * area.js — lógica partilhada pelas páginas de cada área
 *
 * TODO: quando os headers forem definidos, adicionar:
 *  - renderHeaders(columns) → injeta <th> na tabela
 *  - renderRows(records)    → injeta <tr> no tbody
 *  - renderForm(columns)    → injeta campos no modal
 *  - uploadExcel / uploadPDF → POST /[area]/import/excel|pdf
 */

// Detecta a área actual a partir do URL (ex: /compliance → "compliance")
const areaPath = window.location.pathname.split("/")[1];

// Carrega os registos ao abrir a página
document.addEventListener("DOMContentLoaded", async () => {
    await loadRecords();
    setupImportButtons();
    setupNewRecordButton();
});


async function loadRecords() {
    const res = await apiFetch(`/${areaPath}/`);
    if (!res) return;

    const data = await res.json();
    const records = data.records || [];

    const emptyMsg = document.getElementById("empty-msg");
    emptyMsg.classList.toggle("hidden", records.length > 0);

    // TODO: renderizar colunas e linhas quando os headers estiverem definidos
}


function setupImportButtons() {
    document.getElementById("upload-excel").addEventListener("change", async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        const token = Auth.getToken();
        const res = await fetch(`/${areaPath}/import/excel`, {
            method: "POST",
            headers: token ? { Authorization: `Bearer ${token}` } : {},
            body: formData,
        });

        const data = await res.json();
        alert(`Importados: ${data.imported} registos.`);
        await loadRecords();
    });

    document.getElementById("upload-pdf").addEventListener("change", async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        const token = Auth.getToken();
        const res = await fetch(`/${areaPath}/import/pdf`, {
            method: "POST",
            headers: token ? { Authorization: `Bearer ${token}` } : {},
            body: formData,
        });

        const data = await res.json();
        alert(`PDF processado: ${data.pages} páginas.`);
    });
}


function setupNewRecordButton() {
    document.getElementById("btn-new-record").addEventListener("click", () => {
        document.getElementById("modal-title").textContent = "Novo registo";
        document.getElementById("modal-record").classList.remove("hidden");
    });

    document.getElementById("btn-cancel").addEventListener("click", () => {
        document.getElementById("modal-record").classList.add("hidden");
    });

    document.getElementById("btn-save").addEventListener("click", async () => {
        // TODO: recolher valores do formulário e POST /[area]/
        document.getElementById("modal-record").classList.add("hidden");
    });
}
