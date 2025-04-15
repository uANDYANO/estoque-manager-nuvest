Comandos para gerar o app.py
pip freeze > requirements.txt
pyinstaller --noconfirm --onefile --console --add-data "C:\Users\ti.COMRIO\asalviano\Desktop\Estoque Manager\estoque_manager_web2\static;static/" --add-data "C:\Users\ti.COMRIO\asalviano\Desktop\Estoque Manager\estoque_manager_web2\templates;templates/"  "C:\Users\ti.COMRIO\asalviano\Desktop\Estoque Manager\estoque_manager_web2\app.py"

📦 Estoque Manager Web - Deploy em Produção (Windows Server)
✅ Requisitos

    Python 3.10+ instalado no servidor

    MySQL (servidor local ou remoto)

    Git (opcional, mas recomendado)

    Node.js (para build de frontend)

    NSSM (para rodar o app como serviço no Windows)

🚀 Etapas do Deploy
1. 📁 Estrutura do Projeto

estoque_manager_web/
│
├── app.py
├── config.py
├── models.py
├── ...
├── templates/             → Arquivos HTML originais
├── static/
│   ├── css/               → Estilos CSS
│   ├── js/                → Scripts JavaScript
│   └── img/               → Imagens
├── prod/                  → Arquivos otimizados para produção
│   ├── templates/
│   └── static/
│       ├── css/
│       ├── js/
│       └── img/
├── criar_usuario.py       → Script para criação manual de usuários
├── atualizar_senha.py     → Script para redefinir senha
├── start_app.bat          → Script para iniciar a aplicação
├── requirements.txt
└── README.md

2. ⚙️ Instalação do ambiente Python

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

3. 🔧 Configuração do Banco de Dados

    Verifique se config.py está com os dados corretos de conexão com o MySQL.

    Execute os scripts SQL para criação de tabelas e dados iniciais.

    Importe os dados de produção se necessário.

4. 🧪 Criação de usuários

venv\Scripts\activate
python criar_usuario.py

5. 🖼️ Otimização do Frontend (HTML, CSS, JS, IMG)

npm install
npm run build

    Os arquivos serão copiados/minificados para a pasta prod/.

    O sistema deve ser apontado para usar os arquivos de prod/templates e prod/static.

6. ▶️ Teste local (modo desenvolvimento)

venv\Scripts\activate
python app.py

7. ⚙️ Configuração como Serviço no Windows (NSSM)

    Baixe e instale o NSSM.

    Crie um novo serviço:

nssm install EstoqueManager

    Path: C:\EstoqueManager\venv\Scripts\python.exe

    Arguments: app.py

    Startup directory: C:\EstoqueManager

    Inicie o serviço:

nssm start EstoqueManager

8. 🌐 Acesso via IP fixo

    Edite app.py e adiciona no final:

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

    Configure o firewall do Windows para permitir a porta 5000 (ou a que escolher).

    Acesse de outro dispositivo pela URL: http://<ip-do-servidor>:5000

9. 🔒 Segurança

    Sessões expiram após inatividade (configurado).

    Logs com nome e ID do usuário ativo.

    Tela de login segura e estilizada.

    Código em produção minificado e ofuscado.

10. 🧹 Manutenção

    Para redefinir senhas:

python atualizar_senha.py

    Para parar o sistema:

nssm stop EstoqueManager

🛡️ Boas práticas seguidas

    Estrutura MVC organizada

    Histórico de ações por usuário

    Controle de login/logout com Flask-Login

    Arquivos estáticos otimizados

    Deploy como serviço Windows

    Exportações em Excel

    Dashboard e gráficos interativos