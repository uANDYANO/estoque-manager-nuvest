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

### 1. Clone o repositório
```bash
git clone https://github.com/uANDYANO/estoque-manager-nuvest.git
cd estoque-manager
```
### 2. Crie o ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate
```
### 3. Instale as dependências
```bash
pip install -r requirements.txt
```
### 🔐 Variáveis de Ambiente
```bash
Crie um arquivo .env na raiz do projeto com as seguintes variáveis:

FLASK_SECRET_KEY=sua_chave_segura
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=suasenha
DATABASE_NAME=estoque_manager
```
### 🧪 Executar em Desenvolvimento
```bash
python app.py

Acesse: http://localhost:5000
```

### 🏭 Deploy em Produção (Windows)
```bash
Usando NSSM (Non-Sucking Service Manager)

    Gere o .exe com auto-py-to-exe ou use diretamente o app.py.

    Crie um .bat de inicialização:

@echo off
cd /d C:\EstoqueManager
call venv\Scripts\activate
python app.py

    Configure no NSSM:

Path: C:\EstoqueManager\venv\Scripts\python.exe
Arguments: app.py
Startup directory: C:\EstoqueManager
```
### 💾 Backup Diário (MySQL)
```bash
Você pode usar o Agendador de Tarefas do Windows com PowerShell para backup automático.

Script de exemplo disponível em:
/scripts/backup_mysql.ps1
```

### 👨‍💻 Criar Usuário
```bash
python criar_usuario.py
```

### 🔒 Atualizar Senha
```bash
python atualizar_senha.py
```

### 📁 Estrutura de Pastas
```bash
/templates/               → Arquivos HTML (Jinja2)
/static/css/              → Estilos CSS
/static/js/               → Scripts JS
/static/img/              → Imagens
/app.py                   → Arquivo principal da aplicação
/.env                     → Variáveis de ambiente
/requirements.txt         → Dependências Python
```

### 🖼️ Capturas de Tela

<img src="https://github.com/uANDYANO/estoque-manager-nuvest/blob/main/static/img/login-page.png" alt="login">
    
<img src="https://github.com/uANDYANO/estoque-manager-nuvest/blob/main/static/img/dashboard-page.png" alt="dashborad">


### 🔒 Notas de Segurança
```bash
    Nunca envie o arquivo .env para o GitHub (adicione ao .gitignore)

    Use senhas seguras e altere FLASK_SECRET_KEY

    Restrinja acesso ao servidor de produção

    Faça backups frequentes

    Utilize ambientes separados para desenvolvimento e produção
```
### 💼 Licença
```bash
Este projeto está licenciado sob a MIT License.
Você pode usá-lo, modificá-lo e distribuí-lo livremente, com os devidos créditos.
```
👨‍💼 Desenvolvido por

Anderson Salviano
📧 andyanodev@gmail.com
🔗 github.com/andyanodev
