from flask_login import LoginManager
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from datetime import timedelta
import pandas as pd
from io import BytesIO
from pytz import timezone
from copy import deepcopy
from sqlalchemy import and_
from dotenv import load_dotenv
import os

load_dotenv()

# Carregar as variáveis de ambiente
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# URI do banco MySQL com PyMySQL
db_user = os.getenv("DATABASE_USER")
db_pass = os.getenv("DATABASE_PASSWORD")
db_host = os.getenv("DATABASE_HOST")
db_port = os.getenv("DATABASE_PORT")
db_name = os.getenv("DATABASE_NAME")

# Configuração da conexão com MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # tempo de inatividade permitido
app.config['SESSION_PERMANENT'] = True

db = SQLAlchemy(app)

def now_brazil():
    return datetime.now(timezone('America/Sao_Paulo'))

login_manager = LoginManager(app)
login_manager.login_view = 'login'  # redirecionar para login se não autenticado
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# ----------------- MODELOS ----------------- #

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

class Funcionario(db.Model):
    __tablename__ = 'funcionarios'
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(100))

    funcao = db.Column(db.String(100))
    admissao = db.Column(db.Date)
    ativo = db.Column(db.Boolean, default=True)
    unidade_id = db.Column(db.Integer, db.ForeignKey('unidades.id'))
    unidade = db.relationship('Unidade', back_populates='funcionarios')

class Uniforme(db.Model):
    __tablename__ = 'uniformes'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(100))
    tamanho = db.Column(db.String(10))
    quantidade = db.Column(db.Integer)
    status = db.Column(db.String(50))
    ativo = db.Column(db.Boolean, default=True)

class Movimentacao(db.Model):
    __tablename__ = 'movimentacao_uniformes'
    id = db.Column(db.Integer, primary_key=True)
    nome_funcionario = db.Column(db.String(100))
    matricula = db.Column(db.String(50))
    uniforme_id = db.Column(db.Integer, db.ForeignKey('uniformes.id'))
    uniforme = db.relationship('Uniforme', backref='movimentacoes') #integracao com a tabela uniformes
    tamanho = db.Column(db.String(10))
    quantidade = db.Column(db.Integer)
    status = db.Column(db.String(50))
    movimento = db.Column(db.String(50))  # entrega ou devolucao
    data_entrega = db.Column(db.Date)
    data_registro = db.Column(db.DateTime, default=now_brazil)
    unidade_id = db.Column(db.Integer, db.ForeignKey('unidades.id'))
    unidade = db.relationship('Unidade', backref='movimentacoes')


class EntradaEstoque(db.Model):
    __tablename__ = 'entradas_estoque'
    id = db.Column(db.Integer, primary_key=True)
    uniforme_id = db.Column(db.Integer, db.ForeignKey('uniformes.id'))
    quantidade = db.Column(db.Integer)
    motivo = db.Column(db.String(255))
    nota_fiscal = db.Column(db.String(100))
    data_entrada = db.Column(db.Date)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=True)
    tamanho = db.Column(db.String(20), nullable=True)
    ativo = db.Column(db.Boolean, default=True)

    uniforme = db.relationship('Uniforme', backref='entradas')

class HistoricoAcao(db.Model):
    __tablename__ = 'historico_acoes'
    id = db.Column(db.Integer, primary_key=True)
    entidade = db.Column(db.String(50))  # 'Funcionario', 'Uniforme', etc.
    entidade_id = db.Column(db.Integer)  # ID do item
    acao = db.Column(db.String(50))  # 'editar', 'inativar', etc.
    descricao = db.Column(db.Text)  # detalhes da ação
    timestamp = db.Column(db.DateTime, default=now_brazil)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    usuario_nome = db.Column(db.String(255))
    
class Unidade(db.Model):
    __tablename__ = 'unidades'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False, unique=True)

    # Relacionamento com funcionários
    funcionarios = db.relationship('Funcionario', back_populates='unidade')

# ----------------- ROTAS INICIAIS ----------------- #

@app.route('/')
@login_required
def index():
    total_funcionarios_ativos = Funcionario.query.filter_by(ativo=True).count()
    total_funcionarios_inativos = Funcionario.query.filter_by(ativo=False).count()

    total_uniformes_ativos = db.session.query(db.func.sum(Uniforme.quantidade)).filter_by(ativo=True).scalar() or 0
    total_uniformes_inativos = db.session.query(db.func.sum(Uniforme.quantidade)).filter_by(ativo=False).scalar() or 0

    total_mov_ativas = Movimentacao.query.filter(Movimentacao.movimento != 'Cancelado').count()
    total_mov_canceladas = Movimentacao.query.filter(Movimentacao.movimento == 'Cancelado').count()

    total_entradas_ativas = EntradaEstoque.query.filter_by(ativo=True).count()
    total_entradas_canceladas = EntradaEstoque.query.filter_by(ativo=False).count()

    return render_template(
        'index.html',
        dados_resumo={
            "funcionarios": {"ativos": total_funcionarios_ativos, "inativos": total_funcionarios_inativos},
            "uniformes": {"ativos": total_uniformes_ativos, "inativos": total_uniformes_inativos},
            "movimentacoes": {"ativas": total_mov_ativas, "canceladas": total_mov_canceladas},
            "entradas": {"ativas": total_entradas_ativas, "canceladas": total_entradas_canceladas}
        }
    )

# ----------------- ROTAS DE LOGIN ----------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(username=username, ativo=True).first()

        if usuario and usuario.verificar_senha(senha):
            login_user(usuario)
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    expirado = session.pop('expirado', False)  # pega e remove a flag

    logout_user()
    if expirado:
        flash('Sua sessão expirou por inatividade.', 'warning')
    else:
        flash('Você saiu da sessão.', 'info')

    return redirect(url_for('login'))

@app.before_request
def verificar_sessao_expirada():
    if current_user.is_authenticated:
        session.modified = True  # mantém a sessão ativa com atividade
    elif request.endpoint not in ('login', 'static'):
        # Se a sessão expirou, e ele tentou acessar algo sem estar logado:
        session['expirado'] = True

# ----------------- ROTAS FUNCIONARIOS ----------------- #

@app.route('/funcionarios', methods=['GET', 'POST'])
@login_required
def funcionarios():
    unidades = Unidade.query.order_by(Unidade.nome).all()

    if request.method == 'POST':
        nome = request.form['nome']
        matricula = request.form['matricula']
        unidade_id = int(request.form['unidade_id'])
        funcao = request.form['funcao']
        admissao = datetime.strptime(request.form['admissao'], '%Y-%m-%d')

        if Funcionario.query.filter_by(matricula=matricula).first():
            flash('Matrícula já cadastrada. Por favor, utilize outra.')
            return redirect(url_for('funcionarios'))

        novo = Funcionario(nome=nome, matricula=matricula, unidade_id=unidade_id,
                           funcao=funcao, admissao=admissao)
        db.session.add(novo)
        db.session.commit()

        historico = HistoricoAcao(
            acao='criar',
            entidade='funcionario',
            entidade_id=novo.id,
            descricao=f'Funcionário criado: {nome} - Matrícula {matricula} (ID {novo.id})',
            usuario_id=current_user.id,
            usuario_nome=current_user.nome
        )
        db.session.add(historico)
        db.session.commit()

        flash('Funcionário cadastrado com sucesso.')
        return redirect(url_for('funcionarios'))

    filtro_nome = request.args.get('filtro_nome', '').strip()
    filtro_matricula = request.args.get('filtro_matricula', '').strip()
    filtro_unidade_id = request.args.get('filtro_unidade_id', type=int)
    pagina = request.args.get('pagina', 1, type=int)

    query = Funcionario.query.filter_by(ativo=True)
    if filtro_nome:
        query = query.filter(Funcionario.nome.ilike(f"%{filtro_nome}%"))
    if filtro_matricula:
        query = query.filter(Funcionario.matricula.ilike(f"%{filtro_matricula}%"))
    if filtro_unidade_id:
        query = query.filter(Funcionario.unidade_id == filtro_unidade_id)

    funcionarios = query.order_by(Funcionario.nome.asc()).paginate(page=pagina, per_page=50)

    unidades = Unidade.query.order_by(Unidade.nome).all()

    return render_template(
        'funcionarios.html',
        funcionarios=funcionarios,
        filtro_nome=filtro_nome,
        filtro_matricula=filtro_matricula,
        filtro_unidade_id=filtro_unidade_id,
        unidades=unidades
    )


@app.route('/funcionarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_funcionario(id):
    funcionario = Funcionario.query.get_or_404(id)
    unidades = Unidade.query.order_by(Unidade.nome).all()

    if request.method == 'POST':
        funcionario_antigo = deepcopy(funcionario)

        funcionario.nome = request.form['nome']
        funcionario.unidade_id = request.form['unidade_id']
        funcionario.funcao = request.form['funcao']
        funcionario.admissao = datetime.strptime(request.form['admissao'], '%Y-%m-%d')
        db.session.commit()

        def gerar_descricao_edicao_funcionario(antigo, novo):
            campos = ['nome', 'unidade_id', 'funcao', 'admissao']
            descricao = []
            for campo in campos:
                valor_antigo = getattr(antigo, campo)
                valor_novo = getattr(novo, campo)

                if isinstance(valor_antigo, datetime):
                    valor_antigo = valor_antigo.strftime('%d/%m/%Y')
                if isinstance(valor_novo, datetime):
                    valor_novo = valor_novo.strftime('%d/%m/%Y')

                if valor_antigo != valor_novo:
                    descricao.append(f"- {campo.capitalize()}: \"{valor_antigo}\" → \"{valor_novo}\"")

            if descricao:
                return f"Funcionário editado (ID: {novo.id}):\n" + "\n".join(descricao)
            else:
                return f"Funcionário editado (ID: {novo.id}), mas nenhuma informação foi alterada."

        descricao = gerar_descricao_edicao_funcionario(funcionario_antigo, funcionario)

        historico = HistoricoAcao(
            acao='editar',
            entidade='funcionario',
            entidade_id=funcionario.id,
            descricao=descricao,
            usuario_id=current_user.id,
            usuario_nome=current_user.nome
        )
        db.session.add(historico)
        db.session.commit()

        flash('Funcionário atualizado com sucesso!')
        return redirect(url_for('funcionarios'))

    return render_template('editar_funcionario.html', funcionario=funcionario, unidades=unidades)

@app.route('/funcionarios/inativar/<int:id>', methods=['POST'])
@login_required
def inativar_funcionario(id):
    funcionario = Funcionario.query.get_or_404(id)
    funcionario.ativo = False
    db.session.commit()

    descricao = (
        f"Funcionário inativado:\n"
        f"- Nome: {funcionario.nome}\n"
        f"- Matrícula: {funcionario.matricula}\n"
        f"- Unidade: {funcionario.unidade.nome}"
    )

    historico = HistoricoAcao(
        acao='inativar',
        entidade='funcionario',
        entidade_id=funcionario.id,
        descricao=descricao,
        usuario_id=current_user.id,
        usuario_nome=current_user.nome
    )
    db.session.add(historico)
    db.session.commit()

    flash('Funcionário inativado.')
    return redirect(url_for('funcionarios'))

# ----------------- ROTAS UNIFORMES ----------------- #

@app.route('/uniformes', methods=['GET', 'POST'])
@login_required
def uniformes():
    if request.method == 'POST':
        tipo = request.form['tipo']
        tamanho = request.form['tamanho']
        quantidade = request.form['quantidade']
        status = request.form['status']

        novo_uniforme = Uniforme(tipo=tipo, tamanho=tamanho, quantidade=quantidade, status=status)
        db.session.add(novo_uniforme)
        db.session.commit()

        # Registro no histórico
        registro = HistoricoAcao(
            entidade='uniforme',
            entidade_id=novo_uniforme.id,
            acao='criar',
            descricao=f'Uniforme criado: Tipo "{tipo}", Tamanho "{tamanho}", Quantidade {quantidade}, Status "{status}" (ID {novo_uniforme.id})',
            usuario_id=current_user.id,
            usuario_nome=current_user.nome
        )
        db.session.add(registro)
        db.session.commit()

        flash('Uniforme cadastrado com sucesso!')
        return redirect(url_for('uniformes'))

    # Busca todos os uniformes ativos
    uniformes = Uniforme.query.filter_by(ativo=True).all()

    # Cálculo dos dados para os cards de resumo
    total_itens = sum(u.quantidade for u in uniformes)
    total_tipos = len(set((u.tipo, u.tamanho, u.status) for u in uniformes))
    total_novos = sum(1 for u in uniformes if u.status == 'Novo')
    total_usados = sum(1 for u in uniformes if u.status == 'Usado')
    quantidade_baixa = sum(1 for u in uniformes if u.quantidade < 100)

    return render_template(
        'uniformes.html',
        uniformes=uniformes,
        total_itens=total_itens,
        total_tipos=total_tipos,
        total_novos=total_novos,
        total_usados=total_usados,
        quantidade_baixa=quantidade_baixa
    )

@app.route('/uniformes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_uniforme(id):
    uniforme = Uniforme.query.get_or_404(id)

    if request.method == 'POST':
        uniforme_antigo = deepcopy(uniforme)

        uniforme.tipo = request.form['tipo']
        uniforme.tamanho = request.form['tamanho']
        uniforme.quantidade = int(request.form['quantidade'])
        uniforme.status = request.form['status']
        db.session.commit()

        # Gerar descrição detalhada
        def gerar_descricao_edicao_uniforme(antigo, novo):
            campos = ['tipo', 'tamanho', 'status']
            descricao = []

            for campo in campos:
                val_antigo = getattr(antigo, campo)
                val_novo = getattr(novo, campo)
                if val_antigo != val_novo:
                    descricao.append(f'- {campo.capitalize()}: "{val_antigo}" → "{val_novo}"')

            # Verifica se houve alteração na quantidade manualmente
            if antigo.quantidade != novo.quantidade:
                diff = novo.quantidade - antigo.quantidade
                if diff > 0:
                    descricao.append(f'- Quantidade aumentada manualmente em {diff} (de {antigo.quantidade} para {novo.quantidade})')
                elif diff < 0:
                    descricao.append(f'- Quantidade reduzida manualmente em {abs(diff)} (de {antigo.quantidade} para {novo.quantidade})')

            if not descricao:
                return f'Uniforme (ID {novo.id}) editado, mas sem alterações detectadas.'
            return f'Uniforme (ID {novo.id}) editado:\n' + '\n'.join(descricao)

        descricao = gerar_descricao_edicao_uniforme(uniforme_antigo, uniforme)

        registro = HistoricoAcao(
            entidade='Uniforme',
            entidade_id=uniforme.id,
            acao='editar',
            descricao=descricao,
            usuario_id=current_user.id,
            usuario_nome=current_user.nome
        )
        db.session.add(registro)
        db.session.commit()

        flash('Uniforme atualizado com sucesso!')
        return redirect(url_for('uniformes'))

    return render_template('editar_uniforme.html', uniforme=uniforme)

@app.route('/uniformes/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_uniforme(id):
    uniforme = Uniforme.query.get_or_404(id)
    uniforme.ativo = False
    db.session.commit()

    descricao = (
        f'Uniforme inativado (ID {uniforme.id}):\n'
        f'- Tipo: {uniforme.tipo}\n'
        f'- Tamanho: {uniforme.tamanho}\n'
        f'- Status: {uniforme.status}\n'
        f'- Quantidade atual: {uniforme.quantidade}'
    )

    registro = HistoricoAcao(
        entidade='Uniforme',
        entidade_id=uniforme.id,
        acao='inativar',
        descricao=descricao,
        usuario_id=current_user.id,
        usuario_nome=current_user.nome
    )
    db.session.add(registro)
    db.session.commit()

    flash('Uniforme inativado com sucesso.')
    return redirect(url_for('uniformes'))

# ----------------- ROTAS CONTROLE DE ESTOQUE ----------------- #

@app.route('/entradas-estoque', methods=['GET', 'POST'])
@login_required
def entradas_estoque():
    uniformes = Uniforme.query.filter_by(ativo=True).all()

    if request.method == 'POST':
        uniforme_id = request.form['uniforme_id']
        quantidade = int(request.form['quantidade'])
        motivo = request.form['motivo']
        nota_fiscal = request.form['nota_fiscal']
        data_entrada_str = request.form['data_entrada']
        data_entrada = datetime.strptime(data_entrada_str, '%Y-%m-%d')

        uniforme = Uniforme.query.get(uniforme_id)
        if not uniforme:
            flash('Uniforme não encontrado.', 'danger')
            return redirect(url_for('entradas_estoque'))

        # Atualiza o estoque
        uniforme.quantidade += quantidade

        nova_entrada = EntradaEstoque(
            uniforme_id=uniforme_id,
            quantidade=quantidade,
            motivo=motivo,
            nota_fiscal=nota_fiscal,
            data_entrada=data_entrada,
            data_registro=datetime.now(),
            status=uniforme.status,
            tamanho=uniforme.tamanho,
            ativo=True
        )

        db.session.add(nova_entrada)
        db.session.flush()

        # Registro no log
        registro = HistoricoAcao(
            entidade='EntradaEstoque',
            entidade_id=nova_entrada.id,
            acao='criar',
            descricao=(
                f'Entrada registrada: {quantidade} unidades de "{uniforme.tipo}" '
                f'(Tamanho: {uniforme.tamanho}, Status: {uniforme.status}) '
                f'por motivo "{motivo}", NF: {nota_fiscal}, '
                f'Data: {data_entrada_str}'
            ),
            usuario_id=current_user.id,
            usuario_nome=current_user.nome
        )
        db.session.add(registro)

        db.session.commit()
        flash('Entrada de estoque registrada com sucesso.', 'success')
        return redirect(url_for('entradas_estoque'))

    # Filtros da URL
    filtro_tipo = request.args.get('filtro_tipo')
    filtro_tamanho = request.args.get('filtro_tamanho')
    filtro_cancelado = request.args.get('filtro_cancelado', 'todos')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    entradas_query = EntradaEstoque.query.join(Uniforme)

    if filtro_tipo:
        entradas_query = entradas_query.filter(Uniforme.tipo == filtro_tipo)

    if filtro_tamanho:
        entradas_query = entradas_query.filter(Uniforme.tamanho == filtro_tamanho)

    if filtro_cancelado == 'ativos':
        entradas_query = entradas_query.filter(EntradaEstoque.ativo == True)
    elif filtro_cancelado == 'inativos':
        entradas_query = entradas_query.filter(EntradaEstoque.ativo == False)

    if data_inicio:
        data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
        entradas_query = entradas_query.filter(EntradaEstoque.data_entrada >= data_inicio_dt)

    if data_fim:
        data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
        entradas_query = entradas_query.filter(EntradaEstoque.data_entrada <= data_fim_dt)

    pagina = request.args.get('pagina', 1, type=int)
    entradas = entradas_query.order_by(EntradaEstoque.data_registro.desc()).paginate(page=pagina, per_page=50)

    tipos_uniforme = [u.tipo for u in Uniforme.query.with_entities(Uniforme.tipo).filter(Uniforme.ativo == True).distinct().all()]
    tamanhos_uniforme = [u.tamanho for u in Uniforme.query.with_entities(Uniforme.tamanho).filter(Uniforme.ativo == True).distinct().all()]

    return render_template(
        'entradas_estoque.html',
        uniformes=uniformes,
        entradas=entradas,
        tipos_uniforme=tipos_uniforme,
        tamanhos_uniforme=tamanhos_uniforme,
        filtro_cancelado=filtro_cancelado
    )

@app.route('/inativar_entrada_estoque/<int:entrada_id>', methods=['POST'])
@login_required
def inativar_entrada_estoque(entrada_id):
    entrada = db.session.get(EntradaEstoque, entrada_id)
    if entrada and entrada.ativo:
        uniforme = entrada.uniforme

        if uniforme.quantidade < entrada.quantidade:
            flash(f"Não é possível cancelar a entrada. O estoque atual de '{uniforme.tipo}' (tamanho {uniforme.tamanho}) é insuficiente.", 'danger')
            return redirect(url_for('entradas_estoque'))

        # Subtrai do estoque e inativa entrada
        uniforme.quantidade -= entrada.quantidade
        entrada.ativo = False
        entrada.data_registro = datetime.now()

        # Registro no log
        registro = HistoricoAcao(
            entidade='EntradaEstoque',
            entidade_id=entrada.id,
            acao='cancelar',
            descricao=(
                f'Entrada de estoque cancelada: {entrada.quantidade} unidades de "{uniforme.tipo}" '
                f'(Tamanho: {uniforme.tamanho}, Status: {uniforme.status}), '
                f'Motivo original: "{entrada.motivo}", NF: {entrada.nota_fiscal}, '
                f'Data original: {entrada.data_entrada.strftime("%d/%m/%Y")}'
            ),
            usuario_id=current_user.id,
            usuario_nome=current_user.nome
        )
        db.session.add(registro)

        db.session.commit()
        flash('Entrada cancelada com sucesso.', 'success')
    else:
        flash('Entrada não encontrada ou já está cancelada.', 'danger')
    return redirect(url_for('entradas_estoque'))

# ----------------- ROTAS MOVIMENTACOES ----------------- #

@app.route('/movimentacoes', methods=['GET', 'POST'])
@login_required
def movimentacoes():
    filtro_matricula = request.args.get('filtro_matricula', '')
    filtro_unidade_id = request.args.get('filtro_unidade', '')
    filtro_movimento = request.args.get('filtro_movimento', '')
    filtro_tipo_uniforme = request.args.get('filtro_tipo_uniforme', '')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = 50

    query = Movimentacao.query.join(Uniforme).join(Unidade)

    if filtro_matricula:
        query = query.filter(Movimentacao.matricula.contains(filtro_matricula))
    if filtro_unidade_id:
        query = query.filter(Movimentacao.unidade_id == int(filtro_unidade_id))
    if filtro_movimento:
        query = query.filter(Movimentacao.movimento == filtro_movimento)
    if filtro_tipo_uniforme:
        query = query.filter(Uniforme.tipo == filtro_tipo_uniforme)
    if data_inicio:
        query = query.filter(Movimentacao.data_entrega >= data_inicio)
    if data_fim:
        query = query.filter(Movimentacao.data_entrega <= data_fim)

    movimentacoes_paginadas = query.order_by(Movimentacao.data_registro.desc()).paginate(page=pagina, per_page=por_pagina)

    uniformes = Uniforme.query.filter_by(ativo=True).all()
    tipos_uniforme = db.session.query(Uniforme.tipo).filter(Uniforme.ativo == True).distinct().all()
    unidades = Unidade.query.order_by(Unidade.nome).all()

    if request.method == 'POST':
        matricula = request.form['matricula']
        data_entrega = request.form['data_entrega']
        uniforme_id = request.form['uniforme_id']
        quantidade = int(request.form['quantidade'])
        movimento = request.form['movimento']
        nome_funcionario = request.form['nome_funcionario']
        unidade_id = request.form['unidade_id']
        tamanho = request.form['tamanho']

        uniforme = Uniforme.query.get(uniforme_id)
        unidade = Unidade.query.get(unidade_id)

        if movimento == 'entrega':
            if quantidade > uniforme.quantidade:
                flash(f'Estoque insuficiente: disponível {uniforme.quantidade}, solicitado {quantidade}.')
                return redirect(url_for('movimentacoes'))
            uniforme.quantidade -= quantidade
        elif movimento == 'devolucao':
            uniforme.quantidade += quantidade

        nova_mov = Movimentacao(
            matricula=matricula,
            data_entrega=data_entrega,
            uniforme_id=uniforme_id,
            quantidade=quantidade,
            movimento=movimento,
            nome_funcionario=nome_funcionario,
            unidade_id=unidade_id,
            tamanho=tamanho,
            status=uniforme.status
        )

        db.session.add(nova_mov)
        db.session.commit()

        registro = HistoricoAcao(
            entidade='Movimentacao',
            entidade_id=nova_mov.id,
            acao='criar',
            descricao=(
                f"Movimentação registrada:\n"
                f"- Matrícula: {matricula}\n"
                f"- Funcionário: {nome_funcionario}\n"
                f"- Uniforme: {uniforme.tipo} ({tamanho}) [ID {uniforme.id}]\n"
                f"- Tipo: {movimento.capitalize()}\n"
                f"- Quantidade: {quantidade}\n"
                f"- Unidade: {unidade.nome}\n"
                f"- Data: {data_entrega}"
            ),
            usuario_id=current_user.id,
            usuario_nome=current_user.nome
        )
        db.session.add(registro)
        db.session.commit()

        flash('Movimentação registrada com sucesso.')
        return redirect(url_for('movimentacoes'))

    return render_template(
        'movimentacoes.html',
        movimentacoes=movimentacoes_paginadas,
        uniformes=uniformes,
        tipos_uniforme=[t[0] for t in tipos_uniforme],
        unidades=unidades,
        filtro_matricula=filtro_matricula,
        filtro_unidade=filtro_unidade_id,
        filtro_movimento=filtro_movimento,
        filtro_tipo_uniforme=filtro_tipo_uniforme,
        data_inicio=data_inicio,
        data_fim=data_fim
    )

@app.route('/movimentacoes/cancelar/<int:id>', methods=['POST'])
@login_required
def cancelar_movimentacao(id):
    mov = Movimentacao.query.get_or_404(id)

    if mov.status != 'Cancelado':
        uniforme = Uniforme.query.get(mov.uniforme_id)

        if mov.movimento == 'entrega':
            uniforme.quantidade += mov.quantidade
        elif mov.movimento == 'devolucao':
            uniforme.quantidade -= mov.quantidade

        mov.movimento = 'Cancelado'
        db.session.commit()

        # Histórico
        descricao = (
            f"Movimentação cancelada:\n"
            f"- ID da movimentação: {mov.id}\n"
            f"- Funcionário: {mov.nome_funcionario} (Matrícula: {mov.matricula})\n"
            f"- Uniforme: {uniforme.tipo} ({mov.tamanho})\n"
            f"- Tipo original: {mov.movimento}\n"
            f"- Quantidade: {mov.quantidade}\n"
            f"- Unidade: {mov.unidade.nome}\n"
            f"- Data original: {mov.data_entrega}"
        )

        registro = HistoricoAcao(
            entidade='Movimentacao',
            entidade_id=mov.id,
            acao='cancelar',
            descricao=descricao,
            usuario_id=current_user.id,
            usuario_nome=current_user.nome
        )
        db.session.add(registro)
        db.session.commit()

        flash('Movimentação cancelada com sucesso.')

    return redirect(url_for('movimentacoes'))

@app.route('/api/funcionario/<matricula>')
def api_funcionario(matricula):
    funcionario = Funcionario.query.filter_by(matricula=matricula, ativo=True).first()
    if funcionario:
        return {
            'nome': funcionario.nome,
            'unidade': funcionario.unidade.nome,
            'unidade_id': funcionario.unidade.id
        }
    return {}, 404

@app.route('/api/uniforme/<int:id>')
def api_uniforme(id):
    uniforme = Uniforme.query.get(id)
    if uniforme:
        return {'tamanho': uniforme.tamanho}
    return {}, 404

@app.route('/movimentacoes/exportar')
@login_required
def exportar_movimentacoes():
    filtro_matricula = request.args.get('filtro_matricula')
    filtro_unidade_id = request.args.get('filtro_unidade')
    filtro_movimento = request.args.get('filtro_movimento')
    filtro_tipo_uniforme = request.args.get('filtro_tipo_uniforme')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    query = Movimentacao.query.join(Uniforme, Uniforme.id == Movimentacao.uniforme_id)

    if filtro_matricula:
        query = query.filter(Movimentacao.matricula.contains(filtro_matricula))
    if filtro_unidade_id:
        query = query.filter(Movimentacao.unidade_id == int(filtro_unidade_id))
    if filtro_movimento:
        query = query.filter(Movimentacao.movimento == filtro_movimento)
    if filtro_tipo_uniforme:
        query = query.filter(Uniforme.tipo == filtro_tipo_uniforme)
    if data_inicio:
        try:
            inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(Movimentacao.data_entrega >= inicio)
        except ValueError:
            pass
    if data_fim:
        try:
            fim = datetime.strptime(data_fim, '%Y-%m-%d')
            query = query.filter(Movimentacao.data_entrega <= fim)
        except ValueError:
            pass

    movimentacoes = query.order_by(Movimentacao.data_entrega.desc()).all()

    dados = [{
        'Data Registro': m.data_registro.strftime('%d/%m/%Y %H:%M') if m.data_registro else '',
        'Funcionário': m.nome_funcionario,
        'Matrícula': m.matricula,
        'Unidade': m.unidade.nome if m.unidade else '',
        'Uniforme': f"{m.uniforme.tipo}" if m.uniforme else '',
        'Tamanho': m.tamanho,
        'Quantidade': m.quantidade,
        'Status': m.status,
        'Movimento': m.movimento,
        'Data de Entrega': m.data_entrega.strftime('%d/%m/%Y') if m.data_entrega else ''
    } for m in movimentacoes]

    df = pd.DataFrame(dados)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Movimentacoes')

    output.seek(0)
    return send_file(output, download_name='movimentacoes.xlsx', as_attachment=True)

if __name__ == '__main__':
    #para desenvolvimento
    app.run(debug=True, port=5000)
    #para producao
    #app.run(host='192.168.1.202', port=5000, debug=True)
