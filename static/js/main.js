// ========== GLOBAL ==========
document.addEventListener('DOMContentLoaded', function () {
    exibirModalFlash();
    atualizarCamposUniformeEntrada();
    inicializarFiltrosUniformes();
});

// ---------- Modal Flash (usado em todas as abas) ----------
function exibirModalFlash() {
    const flashModalElement = document.getElementById('flashModal');
    const flashMessagesExist = flashModalElement?.querySelector('.alert') !== null;

    if (flashMessagesExist && flashModalElement) {
        const modal = new bootstrap.Modal(flashModalElement);
        modal.show();
    }
}

// ========== ABA DE ENTRADAS ==========

// ---------- Atualiza campos ao selecionar uniforme ----------
function atualizarCamposUniformeEntrada() {
    const uniformeSelect = document.getElementById('uniformeSelect');
    const statusInput = document.getElementById('statusInput');
    const tamanhoInput = document.getElementById('tamanhoInput');

    if (!uniformeSelect) return;

    const atualizar = () => {
        const selectedOption = uniformeSelect.options[uniformeSelect.selectedIndex];
        statusInput.value = selectedOption.getAttribute('data-status') || "";
        tamanhoInput.value = selectedOption.getAttribute('data-tamanho') || "";
    };

    uniformeSelect.addEventListener('change', atualizar);
    atualizar(); // inicial
}

function toggleFormularioEntrada() {
    const form = document.getElementById('formularioEntrada');
    const botao = document.getElementById('botaoToggleEntrada');

    if (form.style.display === 'none' || form.style.display === '') {
        form.style.display = 'block';
        form.classList.remove('fade-slide-up');
        form.classList.add('fade-slide-down');

        botao.innerHTML = '<i class="bi bi-x-circle me-1"></i> Fechar Formulário';
        botao.classList.remove('btn-primary');
        botao.classList.add('btn-danger');
    } else {
        form.classList.remove('fade-slide-down');
        form.classList.add('fade-slide-up');

        setTimeout(() => {
            form.style.display = 'none';
        }, 400);

        botao.innerHTML = '<i class="bi bi-plus-circle me-1"></i> Nova Entrada de Estoque';
        botao.classList.remove('btn-danger');
        botao.classList.add('btn-primary');
    }
}

// ========== ABA DE MOVIMENTAÇÕES ==========

const matriculaInput = document.getElementById('matricula');
if (matriculaInput) {
    matriculaInput.addEventListener('blur', buscarFuncionarioPorMatricula);
    matriculaInput.addEventListener('input', limparCamposFuncionario);
}

function toggleFormularioMovimentacao() {
    const form = document.getElementById('formularioMovimentacao');
    const botao = document.getElementById('botaoToggleMovimentacao');

    if (form.style.display === 'none' || form.style.display === '') {
        form.style.display = 'block';
        form.classList.remove('fade-slide-up');
        form.classList.add('fade-slide-down');

        botao.innerHTML = '<i class="bi bi-x-circle me-1"></i> Fechar Formulário';
        botao.classList.remove('btn-primary');
        botao.classList.add('btn-danger');
    } else {
        form.classList.remove('fade-slide-down');
        form.classList.add('fade-slide-up');

        // Aguarda a animação antes de esconder
        setTimeout(() => {
            form.style.display = 'none';
        }, 400);

        botao.innerHTML = '<i class="bi bi-plus-circle me-1"></i> Nova Movimentação';
        botao.classList.remove('btn-danger');
        botao.classList.add('btn-primary');
    }
}

// ---------- Buscar funcionário ao digitar matrícula ----------
function buscarFuncionarioPorMatricula() {
    const matricula = this.value;
    fetch(`/api/funcionario/${matricula}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('nomeFuncionario').value = data?.nome || '';
            document.getElementById('unidadeFuncionario').value = data?.unidade || '';
            document.getElementById('unidadeIdFuncionario').value = data?.unidade_id || '';
            if (!data?.nome) alert('Funcionário não encontrado!');
        });
}

// ---------- Limpa campos se matrícula for apagada ----------
function limparCamposFuncionario() {
    if (this.value.trim() === '') {
        document.getElementById('nomeFuncionario').value = '';
        document.getElementById('unidadeFuncionario').value = '';
    }
}

// ---------- Buscar info do uniforme ao selecioná-lo ----------
const uniformeMovSelect = document.getElementById('uniformeSelect');
if (uniformeMovSelect) {
    uniformeMovSelect.addEventListener('change', function () {
        fetch(`/api/uniforme/${this.value}`)
            .then(res => res.json())
            .then(data => {
                document.getElementById('tamanhoUniforme').value = data?.tamanho || '';
                if (!data?.tamanho) alert('Uniforme não encontrado!');
            });
    });

    uniformeMovSelect.addEventListener('input', function () {
        if (this.value === '') {
            document.getElementById('tamanhoUniforme').value = '';
        }
    });
}

// ========== ABA DE UNIFORMES (DASHBOARD) ==========

// ---------- Mostrar/esconder formulário ----------
function toggleFormularioCadastro() {
    const form = document.getElementById('formularioCadastro');
    const botao = document.getElementById('botaoToggleCadastro');

    if (form.classList.contains('ativo')) {
        form.classList.remove('ativo');

        // Altera para estado "fechado"
        botao.innerHTML = '<i class="bi bi-plus-circle me-1"></i> Cadastrar Novo Uniforme';
        botao.classList.remove('btn-danger');
        botao.classList.add('btn-primary');

    } else {
        form.classList.add('ativo');

        // Altera para estado "aberto"
        botao.innerHTML = '<i class="bi bi-x-circle me-1"></i> Fechar Formulário';
        botao.classList.remove('btn-primary');
        botao.classList.add('btn-danger');
    }
}

// ---------- Inicializa os filtros de tipo e tamanho ----------
function inicializarFiltrosUniformes() {
    const tipos = new Set();
    const tamanhos = new Set();

    document.querySelectorAll(".col").forEach(col => {
        const tipo = col.querySelector(".texto-tipo")?.textContent.trim();
        const tamanho = Array.from(col.querySelectorAll(".info-row")).find(row =>
            row.querySelector(".info-label")?.textContent.includes("Tamanho")
        )?.querySelector("span:last-child")?.textContent.trim();

        if (tipo) tipos.add(tipo);
        if (tamanho) tamanhos.add(tamanho);
    });

    const tipoDatalist = document.getElementById("tiposDatalist");
    const tamanhoSelect = document.getElementById("filtroTamanho");

    tipos.forEach(tipo => {
        const option = document.createElement("option");
        option.value = tipo;
        tipoDatalist?.appendChild(option);
    });

    tamanhos.forEach(tamanho => {
        const option = document.createElement("option");
        option.value = tamanho;
        option.textContent = tamanho;
        tamanhoSelect?.appendChild(option);
    });

    filtrarTodosUniformes();
}

// ---------- Animações ----------
function aplicarAnimacaoCard(col, delay = 0) {
    col.classList.remove("fade-out");
    col.style.display = "block";
    col.style.opacity = "0";
    col.style.transform = "translateY(20px)";
    col.style.transition = "none";

    setTimeout(() => {
        col.style.transition = "opacity 0.4s ease, transform 0.4s ease";
        col.style.opacity = "1";
        col.style.transform = "translateY(0)";
    }, delay);
}

function aplicarDesaparecerCard(col) {
    col.style.transition = "opacity 0.3s ease, transform 0.3s ease";
    col.style.opacity = "0";
    col.style.transform = "translateY(10px)";
    setTimeout(() => {
        col.style.display = "none";
    }, 300);
}

// ---------- Filtro principal ----------
function filtrarTodosUniformes() {
    const tipoSelecionado = document.getElementById("filtroTipoInput").value.toLowerCase().trim();
    const tamanhoSelecionado = document.getElementById("filtroTamanho").value.toLowerCase();
    const statusSelecionado = document.getElementById("filtroStatus").value.toLowerCase();

    const cards = document.querySelectorAll(".col");
    let visiveis = 0;

    cards.forEach(col => {
        const tipo = col.querySelector(".texto-tipo")?.textContent.trim().toLowerCase() || "";

        const tamanhoEl = Array.from(col.querySelectorAll(".info-row")).find(row =>
            row.querySelector(".info-label")?.textContent.includes("Tamanho")
        );
        const tamanho = tamanhoEl?.querySelector("span:last-child")?.textContent.trim().toLowerCase() || "";

        const statusEl = Array.from(col.querySelectorAll(".info-row")).find(row =>
            row.querySelector(".info-label")?.textContent.includes("Status")
        );
        const status = statusEl?.querySelector("span.badge")?.textContent.trim().toLowerCase() || "";

        const matchTipo = !tipoSelecionado || tipo.includes(tipoSelecionado);
        const matchTamanho = !tamanhoSelecionado || tamanho === tamanhoSelecionado;
        const matchStatus = !statusSelecionado || status === statusSelecionado;

        if (matchTipo && matchTamanho && matchStatus) {
            aplicarAnimacaoCard(col, visiveis * 60);
            visiveis++;
        } else {
            aplicarDesaparecerCard(col);
        }
    });
}

// ---------- Limpar filtros ----------
function limparFiltrosUniformes() {
    document.getElementById("filtroTipoInput").value = "";
    document.getElementById("filtroTamanho").value = "";
    document.getElementById("filtroStatus").value = "";

    filtrarTodosUniformes();
}

// ========== ABA DE FUNCIONÁRIOS ==========
