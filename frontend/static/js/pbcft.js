/**
 * pbcft.js — PBC/FT: Prevenção de Branqueamento de Capitais e Financiamento do Terrorismo
 */

let records = [];
let fundos  = [];   // tags activas no modal

document.addEventListener("DOMContentLoaded", async () => {
    await loadRecords();
    setupModal();
    setupTagsInput();
    setupPEPToggle();
});


// ============================================================
// Dados
// ============================================================

async function loadRecords() {
    const res = await apiFetch("/pbcft/records");
    if (!res) return;
    records = await res.json();
    renderTable();
}


// ============================================================
// Tabela
// ============================================================

function renderTable() {
    const tbody  = document.getElementById("tbody-pbcft");
    const empty  = document.getElementById("empty-msg");

    tbody.innerHTML = "";

    if (records.length === 0) {
        empty.classList.remove("hidden");
        return;
    }
    empty.classList.add("hidden");

    records.forEach(r => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td class="td-nome">${esc(r.nome)}</td>
            <td class="td-num">${fmtEur(r.investimento)}</td>
            <td>${renderFundos(r.fundos)}</td>
            <td>${renderRisco(r.perfil_risco)}</td>
            <td>${renderPEP(r.is_pep)}</td>
            <td>${renderDocs(r)}</td>
            <td class="td-date">${fmtDate(r.data_entrada_compliance)}</td>
            <td>${renderDecisao(r)}</td>
            <td class="td-actions">
                <button class="btn-secondary btn-sm" onclick="abrirEdicao(${r.id})">Editar</button>
                <button class="btn-danger btn-sm" onclick="eliminarRegisto(${r.id})">Eliminar</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}


// ---- Helpers de renderização ----

function esc(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function fmtEur(val) {
    return new Intl.NumberFormat("pt-PT", { style: "currency", currency: "EUR" }).format(val);
}

function fmtDate(val) {
    if (!val) return "<span class='td-vazio'>—</span>";
    const [y, m, d] = val.split("-");
    return `${d}/${m}/${y}`;
}

function renderFundos(list) {
    if (!list || list.length === 0) return "<span class='td-vazio'>—</span>";
    return list.map(f => `<span class="tag tag-table">${esc(f)}</span>`).join("");
}

function renderRisco(risco) {
    const map = {
        baixo: ["badge-baixo", "Baixo"],
        medio: ["badge-medio", "Médio"],
        alto:  ["badge-alto",  "Alto"],
    };
    const [cls, label] = map[risco] || ["", risco];
    return `<span class="badge ${cls}">${label}</span>`;
}

function renderPEP(isPep) {
    return isPep
        ? `<span class="badge badge-pep">Sim</span>`
        : `<span class="badge badge-nao-pep">Não</span>`;
}

function renderDocs(r) {
    const ic = (ok, title) =>
        `<span class="doc-icon" title="${title}">${ok ? "✅" : "❌"}</span>`;
    return `
        <div class="doc-icons">
            ${ic(r.doc_identificacao, "Doc. identificação")}
            ${ic(r.doc_morada,        "Comp. morada")}
            ${ic(r.doc_rendimentos,   "Comp. rendimentos")}
        </div>`;
}

function renderDecisao(r) {
    if (!r.data_decisao) return "<span class='td-vazio'>—</span>";
    const badgeMap = {
        info_solicitada: ["badge-info-sol", "Info solicitada"],
        aprovado:        ["badge-aprovado", "Aprovado"],
    };
    const [cls, label] = badgeMap[r.tipo_decisao] || ["", ""];
    return `
        <div class="decisao-cell">
            <span class="decisao-data">${fmtDate(r.data_decisao)}</span>
            ${cls ? `<span class="badge ${cls}">${label}</span>` : ""}
        </div>`;
}


// ============================================================
// Modal
// ============================================================

function setupModal() {
    document.getElementById("btn-novo").addEventListener("click",    () => abrirModal());
    document.getElementById("btn-cancelar").addEventListener("click", () => fecharModal());
    document.getElementById("btn-guardar").addEventListener("click",  () => guardarRegisto());

    // Fechar ao clicar no backdrop
    document.getElementById("modal-pbcft").addEventListener("click", e => {
        if (e.target === e.currentTarget) fecharModal();
    });
}

function abrirModal(record = null) {
    fundos = [];

    const isEdit = !!record;
    document.getElementById("modal-title").textContent = isEdit ? "Editar investidor" : "Novo investidor";
    document.getElementById("record-id").value          = isEdit ? record.id : "";
    document.getElementById("f-nome").value             = isEdit ? record.nome : "";
    document.getElementById("f-investimento").value     = isEdit ? record.investimento : "";
    document.getElementById("f-risco").value            = isEdit ? record.perfil_risco : "";
    document.getElementById("f-pep").checked            = isEdit ? record.is_pep : false;
    document.getElementById("f-doc-id").checked         = isEdit ? record.doc_identificacao : false;
    document.getElementById("f-doc-morada").checked     = isEdit ? record.doc_morada : false;
    document.getElementById("f-doc-rendimentos").checked= isEdit ? record.doc_rendimentos : false;
    document.getElementById("f-data-entrada").value     = isEdit ? (record.data_entrada_compliance || "") : "";
    document.getElementById("f-data-decisao").value     = isEdit ? (record.data_decisao || "") : "";
    document.getElementById("f-tipo-decisao").value     = isEdit ? (record.tipo_decisao || "") : "";

    fundos = isEdit ? [...record.fundos] : [];
    renderTagsList();
    updatePEPLabel();

    document.getElementById("modal-pbcft").classList.remove("hidden");
    document.getElementById("f-nome").focus();
}

function fecharModal() {
    document.getElementById("modal-pbcft").classList.add("hidden");
}

function abrirEdicao(id) {
    const record = records.find(r => r.id === id);
    if (record) abrirModal(record);
}

async function eliminarRegisto(id) {
    const record = records.find(r => r.id === id);
    if (!record) return;
    if (!confirm(`Eliminar o registo de "${record.nome}"?`)) return;

    const res = await apiFetch(`/pbcft/${id}`, { method: "DELETE" });
    if (res && (res.ok || res.status === 204)) await loadRecords();
}

async function guardarRegisto() {
    const id   = document.getElementById("record-id").value;
    const nome = document.getElementById("f-nome").value.trim();
    const inv  = parseFloat(document.getElementById("f-investimento").value);
    const risco= document.getElementById("f-risco").value;

    if (!nome) {
        alert("O campo Nome é obrigatório.");
        document.getElementById("f-nome").focus();
        return;
    }
    if (isNaN(inv) || inv < 0) {
        alert("Introduza um valor de investimento válido.");
        document.getElementById("f-investimento").focus();
        return;
    }
    if (!risco) {
        alert("Seleccione o perfil de risco.");
        document.getElementById("f-risco").focus();
        return;
    }

    const body = {
        nome,
        investimento:              inv,
        fundos:                    [...fundos],
        perfil_risco:              risco,
        is_pep:                    document.getElementById("f-pep").checked,
        doc_identificacao:         document.getElementById("f-doc-id").checked,
        doc_morada:                document.getElementById("f-doc-morada").checked,
        doc_rendimentos:           document.getElementById("f-doc-rendimentos").checked,
        data_entrada_compliance:   document.getElementById("f-data-entrada").value || null,
        data_decisao:              document.getElementById("f-data-decisao").value || null,
        tipo_decisao:              document.getElementById("f-tipo-decisao").value || null,
    };

    const url    = id ? `/pbcft/${id}` : "/pbcft/";
    const method = id ? "PUT" : "POST";

    const res = await apiFetch(url, { method, body: JSON.stringify(body) });
    if (res && res.ok) {
        fecharModal();
        await loadRecords();
    } else {
        alert("Erro ao guardar o registo. Tente novamente.");
    }
}


// ============================================================
// Tags input (fundos)
// ============================================================

function setupTagsInput() {
    const input   = document.getElementById("fundo-input");
    const wrapper = document.getElementById("tags-wrapper");

    wrapper.addEventListener("click", () => input.focus());

    input.addEventListener("keydown", e => {
        if (e.key === "Enter" || e.key === ",") {
            e.preventDefault();
            adicionarFundo(input.value);
            input.value = "";
        } else if (e.key === "Backspace" && input.value === "" && fundos.length > 0) {
            fundos.pop();
            renderTagsList();
        }
    });

    input.addEventListener("blur", () => {
        if (input.value.trim()) {
            adicionarFundo(input.value);
            input.value = "";
        }
    });
}

function adicionarFundo(val) {
    const nome = val.trim().replace(/,+$/, "");
    if (nome && !fundos.includes(nome)) {
        fundos.push(nome);
        renderTagsList();
    }
}

function renderTagsList() {
    const list = document.getElementById("tags-list");
    list.innerHTML = fundos
        .map((f, i) => `
            <span class="tag">
                ${esc(f)}
                <span class="tag-remove" onclick="removerFundo(${i})" title="Remover">×</span>
            </span>`)
        .join("");
}

function removerFundo(index) {
    fundos.splice(index, 1);
    renderTagsList();
}


// ============================================================
// Toggle PEP
// ============================================================

function setupPEPToggle() {
    document.getElementById("f-pep").addEventListener("change", updatePEPLabel);
}

function updatePEPLabel() {
    const checked = document.getElementById("f-pep").checked;
    document.getElementById("pep-label").textContent = checked ? "Sim" : "Não";
}
