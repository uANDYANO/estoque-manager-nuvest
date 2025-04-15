      
# 📦 Estoque Manager - Deploy em Produção (Windows Server)

Este documento descreve como fazer o deploy do sistema **Estoque Manager** (desenvolvido com Flask e MySQL) como um serviço contínuo em um ambiente Windows Server 2016 (ou superior). O processo utiliza o PyInstaller para empacotar a aplicação Python em um único arquivo executável (`.exe`) e o NSSM (Non-Sucking Service Manager) para gerenciá-lo como um serviço do Windows.

## ✅ Pré-requisitos

Antes de iniciar o deploy, certifique-se de que os seguintes componentes estejam instalados e configurados no servidor Windows:

*   **Python:** Versão 3.10 ou 3.11 instalada.
*   **MySQL Server:** Instalado e em execução, com o banco de dados do Estoque Manager já criado e configurado.
*   **Pip e Venv:** Ferramentas do Python (`pip` para gerenciamento de pacotes e `venv` para ambientes virtuais) funcionando corretamente.
*   **PyInstaller:** Instalado no ambiente Python. Execute `pip install pyinstaller` se necessário.
*   **NSSM (Non-Sucking Service Manager):** Ferramenta para registrar o `.exe` como um serviço. Baixe a versão mais recente em: [https://nssm.cc/download](https://nssm.cc/download)

## 📁 Estrutura do Projeto (Antes do Build)

A estrutura de diretórios esperada para o projeto antes de empacotar com PyInstaller é:

    

IGNORE_WHEN_COPYING_START
Use code with caution.Markdown
IGNORE_WHEN_COPYING_END

EstoqueManager/
├── app.py # Arquivo principal da aplicação Flask
├── static/ # Arquivos estáticos (CSS, JS, imagens)
│ └── ...
├── templates/ # Templates HTML (Jinja2)
│ └── ...
├── venv/ # Ambiente virtual (criado na Etapa 1)
└── requirements.txt # Lista de dependências Python

      
## ⚙️ Etapas de Deploy

Siga estas etapas para realizar o deploy da aplicação no servidor Windows:

### 1. Criar Ambiente Virtual e Instalar Dependências

No diretório raiz do projeto (`EstoqueManager/`), abra um Prompt de Comando (CMD) ou PowerShell e execute:

```bash
# Criar o ambiente virtual (se ainda não existir)
python -m venv venv

# Ativar o ambiente virtual
venv\Scripts\activate

# Instalar as dependências listadas no requirements.txt
pip install -r requirements.txt

    

IGNORE_WHEN_COPYING_START
Use code with caution.
IGNORE_WHEN_COPYING_END
2. Gerar Arquivo .exe com PyInstaller

Com o ambiente virtual ativado, execute o PyInstaller para empacotar a aplicação. O comando inclui as pastas static e templates no executável:

      
pyinstaller --noconfirm --onefile --console ^
  --add-data "static;static/" ^
  --add-data "templates;templates/" ^
  app.py

    

IGNORE_WHEN_COPYING_START
Use code with caution.Bash
IGNORE_WHEN_COPYING_END

    --noconfirm: Evita confirmações durante o build.

    --onefile: Gera um único arquivo .exe.

    --console: Mantém a janela do console visível quando o .exe é executado diretamente (útil para debug). Remova se preferir --windowed para uma aplicação sem console visível (mas dificulta o debug inicial).

    --add-data "source;destination": Inclui arquivos/pastas não-Python. O formato pasta;pasta/ garante que o conteúdo seja colocado em um diretório relativo com o mesmo nome dentro do pacote.

✅ O executável final (app.exe) estará localizado na pasta dist\ (Ex: EstoqueManager\dist\app.exe).
3. Ajustar app.py para Suportar o Modo Empacotado

Para que o Flask encontre as pastas static e templates quando executado a partir do .exe gerado pelo PyInstaller, adicione o seguinte código no início do seu app.py:

      
import os
import sys
from flask import Flask

# Define o diretório base correto, funcione tanto no modo de script quanto no modo empacotado pelo PyInstaller
if getattr(sys, 'frozen', False):
    # Se rodando como um bundle '.exe' (PyInstaller)
    base_dir = sys._MEIPASS
else:
    # Se rodando como um script '.py' normal
    base_dir = os.path.abspath(os.path.dirname(__file__))

# Inicializa o Flask especificando os caminhos corretos para templates e static
app = Flask(__name__,
            template_folder=os.path.join(base_dir, 'templates'),
            static_folder=os.path.join(base_dir, 'static'))

# --- Restante do seu código Flask ---
# Exemplo:
# @app.route('/')
# def index():
#     return render_template('index.html')
#
# if __name__ == '__main__':
#     # Considere usar Gunicorn ou Waitress em produção ou ajustar host/porta
#     # Para rodar como serviço, o app.run() precisa ser chamado quando o exe é iniciado.
#     # O host '0.0.0.0' permite acesso de outras máquinas na rede.
#     app.run(host='0.0.0.0', port=5000)
# -----------------------------------

    

IGNORE_WHEN_COPYING_START
Use code with caution.Python
IGNORE_WHEN_COPYING_END

Importante: Após fazer essa alteração no app.py, regenere o arquivo .exe usando o comando do PyInstaller (Etapa 2).
4. Instalar NSSM e Criar o Serviço Windows

    Baixe o NSSM: Faça o download do NSSM no link fornecido nos pré-requisitos.

    Extraia: Extraia o arquivo nssm.exe (escolha a versão win32 ou win64 compatível com seu Windows) para um local de fácil acesso (ex: C:\NSSM\).

    Abra o CMD/PowerShell como Administrador: É crucial ter privilégios de administrador.

    Navegue até o diretório do NSSM (ou adicione-o ao PATH do sistema) e execute o comando para instalar um novo serviço:

          
    nssm install <NomeDoServico>

        

    IGNORE_WHEN_COPYING_START

    Use code with caution.Bash
    IGNORE_WHEN_COPYING_END

    Exemplo: nssm install EstoqueManagerService

    Configure o Serviço na Janela do NSSM:

        Aba Application:

            Path: Navegue e selecione o caminho completo para o arquivo app.exe gerado pelo PyInstaller. Ex: C:\Caminho\Para\Projeto\EstoqueManager\dist\app.exe.

            Startup directory: Informe o diretório onde o app.exe está localizado. Ex: C:\Caminho\Para\Projeto\EstoqueManager\dist.

            Arguments: (Opcional) Argumentos a serem passados para o app.exe, se houver.

        Aba Details (Opcional):

            Display name: Nome amigável que aparecerá na lista de Serviços do Windows.

            Description: Descrição do que o serviço faz.

        Aba I/O (Recomendado): Configure arquivos de log para Output (stdout) e Error (stderr). Isso é vital para diagnosticar problemas. Ex: C:\Logs\EstoqueManager_out.log e C:\Logs\EstoqueManager_err.log.

        Aba Exit actions (Recomendado): Configure o reinício automático do serviço em caso de falha (ex: Restart application, com um delay de alguns segundos).

    Clique em "Install service".

    Inicie o Serviço:

        Abra o Painel de Serviços do Windows (execute services.msc).

        Localize o serviço pelo nome que você definiu (ex: EstoqueManagerService).

        Clique com o botão direito e selecione "Iniciar".

        (Opcional) Configure o serviço para iniciar automaticamente com o Windows (clique direito > Propriedades > Tipo de Inicialização: Automático).

5. Configurar Firewall (Se Necessário)

Se o Firewall do Windows estiver ativo no servidor, você precisará criar uma Regra de Entrada para permitir conexões na porta que sua aplicação Flask está escutando (o padrão é a porta 5000, a menos que você tenha configurado outra no app.run() ou via WSGI server).

    Tipo de Regra: Porta

    Protocolo: TCP

    Porta Local Específica: 5000 (ou a porta configurada)

    Ação: Permitir a conexão

    Perfil: Aplique a regra aos perfis de rede apropriados (Domínio, Privado). Use Público com cautela.

6. Acessar a Aplicação no Navegador

Após iniciar o serviço e configurar o firewall, você pode acessar a aplicação Estoque Manager de qualquer computador na mesma rede usando o endereço IP fixo do servidor e a porta configurada:

http://IP_DO_SERVIDOR:5000

Substitua IP_DO_SERVIDOR pelo endereço IP real do seu Windows Server.
🛠️ Troubleshooting

Encontrou problemas? Aqui estão algumas verificações comuns:

    ❗ TemplateNotFound ou Arquivos Estáticos (CSS/JS) não carregam:

        Confirme que as opções --add-data "static;static/" e --add-data "templates;templates/" foram usadas corretamente no comando PyInstaller.

        Verifique se o código de ajuste do base_dir (Etapa 3) está presente e correto no app.py e se o .exe foi gerado após essa modificação.

    ❗ Erro ao iniciar o serviço via NSSM ou o serviço para inesperadamente:

        Verifique os logs: Examine os arquivos de log de stdout e stderr configurados na aba I/O do NSSM. Eles geralmente contêm mensagens de erro detalhadas do Python/Flask.

        Execute manualmente: Pare o serviço no services.msc. Abra um CMD/PowerShell no diretório dist/ e execute .\app.exe diretamente. Observe se há erros no console.

        Verifique permissões: A conta que executa o serviço (padrão: Sistema Local) precisa de permissões para acessar o diretório da aplicação, logs e potencialmente a rede/banco de dados.

    ❗ Aplicação não conecta ao MySQL:

        Confirme que o serviço do MySQL Server está em execução no servidor de banco de dados.

        Verifique se as credenciais de conexão (host, porta, usuário, senha, nome do banco) no código Flask (ou em arquivos de configuração/variáveis de ambiente) estão corretas para o ambiente de produção.

        Certifique-se de que o firewall no servidor MySQL (se separado) e na rede permite conexões do servidor de aplicação para a porta do MySQL (padrão: 3306).

        Teste a conectividade do banco de dados a partir do próprio servidor de aplicação usando uma ferramenta cliente MySQL.

🔐 Segurança

    Garanta que o acesso ao Windows Server seja restrito a pessoal autorizado.

    Configure o serviço NSSM para rodar com uma conta de usuário de privilégios mínimos, se possível, em vez da conta "Sistema Local".

    Nunca armazene senhas ou chaves secretas diretamente no código fonte. Utilize variáveis de ambiente, arquivos de configuração seguros ou um sistema de gerenciamento de segredos.

    Mantenha o Windows Server, Python e todas as bibliotecas (incluindo Flask e conectores de banco de dados) atualizados com os últimos patches de segurança.

    Considere usar HTTPS para proteger a comunicação, especialmente se a aplicação for acessível externamente. Isso geralmente envolve configurar um proxy reverso (como Nginx ou IIS) na frente da aplicação Flask.

    Implemente backups regulares e seguros do banco de dados MySQL.

📝 Sobre o Estoque Manager

O Estoque Manager é um sistema web desenvolvido com Flask (framework Python) e MySQL (banco de dados relacional), projetado para facilitar o controle e gerenciamento de estoque, com foco inicial em uniformes.

Recursos Principais:

    Dashboard interativo para visualização rápida do status do estoque.

    Controle de acesso baseado em usuários.

    Registro de ações e movimentações no sistema (auditoria).

    Funcionalidades para exportar dados e gerar relatórios relevantes.

      
Este `README.md` deve fornecer um guia claro e detalhado para o processo de deploy. Lembre-se de adaptar os caminhos de arquivo (`C:\Caminho\Para\Projeto\`, `C:\Logs\`) e o nome do serviço (`EstoqueManagerService`) conforme a sua configuração específica.

    