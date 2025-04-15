# 🧥 Estoque Manager Nuvest - Sistema de Controle de Uniformes

Sistema web completo para controle de estoque de uniformes, com gestão de funcionários, movimentações, entradas, histórico de ações e login de usuários com sessão segura.

---

## 🚀 Funcionalidades

- Cadastro e edição de funcionários
- Gestão de entradas e saídas de uniformes
- Dashboard visual e responsivo
- Controle de estoque por status e tamanho
- Relatórios exportáveis em Excel
- Registro de ações (log completo)
- Tela de login com controle de sessão
- Controle de permissões por usuário

---

## 🛠️ Requisitos

- Python 3.10 ou superior
- MySQL Server
- Node.js (apenas para build/minificação frontend)
- [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (caso use Cython/Nuitka)

---

## ⚙️ Configuração Inicial

1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/estoque-manager.git
cd estoque-manager

2. Crie o ambiente virtual

python -m venv venv
venv\Scripts\activate

3. Instale as dependências

pip install -r requirements.txt

🔐 Variáveis de Ambiente

Crie um arquivo .env na raiz do projeto com as seguintes variáveis:

FLASK_SECRET_KEY=sua_chave_segura
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=suasenha
DATABASE_NAME=estoque_manager

🧪 Executar em Desenvolvimento

python app.py

Acesse: http://localhost:5000
🏭 Deploy em Produção (Windows)
Usando NSSM

    Gere o .exe com auto-py-to-exe ou use app.py diretamente.

    Crie um .bat de inicialização:

@echo off
cd /d C:\EstoqueManager
call venv\Scripts\activate
python app.py

    Adicione o serviço no NSSM:

        Path: C:\EstoqueManager\venv\Scripts\python.exe

        Arguments: app.py

        Startup directory: C:\EstoqueManager

💾 Backup Diário (MySQL)

Você pode usar o agendador de tarefas com PowerShell para backup automático. Exemplo de script disponível em /scripts/backup_mysql.ps1.
👨‍💻 Criar Usuário

python criar_usuario.py

🔒 Atualizar Senha

python atualizar_senha.py

📁 Estrutura de Pastas

/templates/               → Arquivos HTML (Jinja2)
/static/css/              → Estilos CSS
/static/js/               → Scripts JS
/static/img/              → Imagens
/app.py                   → Arquivo principal da aplicação
/.env                     → Variáveis de ambiente
/requirements.txt         → Dependências Python

👨‍💼 Desenvolvido por

Anderson Salviano
📧 andyanodev@gmail.com
🔗 https://github.com/andyanodev
