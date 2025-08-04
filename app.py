import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_login import login_user, logout_user, login_required, current_user
from models import db, login_manager, User, Aluno, Pagamento, init_app_models
login_manager.login_view = 'login' # Define a rota para o login
app = Flask(__name__)
init_app_models(app, db, login_manager)

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações (pegando do .env para deploy)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'Senha123')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import db, login_manager, User, Aluno, Pagamento, init_app_models

init_app_models(app, db, login_manager)
login_manager.login_view = 'login' # Define a rota para o login

from flask_login import login_user, logout_user, login_required, current_user
from forms import LoginForm, AlunoForm, PagamentoForm


# --- Rotas Básicas ---
@app.route('/')
def index():
    return redirect(url_for('login')) # Redireciona para a tela de login

# --- Rotas de Autenticação ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login realizado com sucesso!', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Login ou senha incorretos.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

# --- Rotas Principais ---
@app.route('/dashboard')
@login_required
def dashboard():
    total_alunos = Aluno.query.count()
    pagamentos_recentes = Pagamento.query.order_by(Pagamento.data_pagamento.desc()).limit(5).all()
    return render_template('dashboard.html', total_alunos=total_alunos, pagamentos_recentes=pagamentos_recentes)

# --- Rotas de Alunos (CRUD) ---
@app.route('/alunos')
@login_required
def lista_alunos():
    alunos = Aluno.query.all()
    return render_template('usuarios.html', alunos=alunos)

@app.route('/alunos/novo', methods=['GET', 'POST'])
@login_required
def adicionar_aluno():
    form = AlunoForm()
    if form.validate_on_submit():
        aluno = Aluno(
            nome=form.nome.data,
            sobrenome=form.sobrenome.data,
            cpf=form.cpf.data,
            telefone=form.telefone.data
        )
        db.session.add(aluno)
        db.session.commit()
        flash('Aluno adicionado com sucesso!', 'success')
        return redirect(url_for('lista_alunos'))
    return render_template('add_usuario.html', form=form, title='Adicionar Aluno')

@app.route('/alunos/<int:aluno_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_aluno(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    form = AlunoForm(obj=aluno)
    if form.validate_on_submit():
        form.populate_obj(aluno)
        db.session.commit()
        flash('Aluno atualizado com sucesso!', 'success')
        return redirect(url_for('lista_alunos'))
    return render_template('edit_usuario.html', form=form, aluno=aluno, title='Editar Aluno')

@app.route('/alunos/<int:aluno_id>/excluir', methods=['POST'])
@login_required
def excluir_aluno(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    db.session.delete(aluno)
    db.session.commit()
    flash('Aluno excluído com sucesso!', 'success')
    return redirect(url_for('lista_alunos'))

# --- Rotas de Pagamentos ---
@app.route('/alunos/<int:aluno_id>/pagamentos')
@login_required
def lista_pagamentos_aluno(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    pagamentos = Pagamento.query.filter_by(aluno_id=aluno.id).order_by(Pagamento.data_pagamento.desc()).all()
    return render_template('pagamentos.html', aluno=aluno, pagamentos=pagamentos)

@app.route('/alunos/<int:aluno_id>/pagamentos/novo', methods=['GET', 'POST'])
@login_required
def adicionar_pagamento(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    form = PagamentoForm()
    if form.validate_on_submit():
        pagamento = Pagamento(
            aluno_id=aluno.id,
            valor=form.valor.data,
            data_vencimento=form.data_vencimento.data,
            status=form.status.data,
            descricao=form.descricao.data
        )
        db.session.add(pagamento)
        db.session.commit()
        flash('Pagamento registrado com sucesso!', 'success')
        return redirect(url_for('lista_pagamentos_aluno', aluno_id=aluno.id))
    return render_template('add_pagamento.html', form=form, aluno=aluno, title='Registrar Pagamento')

@app.route('/pagamentos/<int:pagamento_id>/excluir', methods=['POST'])
@login_required
def excluir_pagamento(pagamento_id):
    pagamento = Pagamento.query.get_or_404(pagamento_id)
    aluno_id = pagamento.aluno_id # Captura o ID do aluno antes de excluir
    db.session.delete(pagamento)
    db.session.commit()
    flash('Pagamento excluído com sucesso!', 'success')
    return redirect(url_for('lista_pagamentos_aluno', aluno_id=aluno_id))


if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Cria as tabelas do banco de dados
        # Opcional: Criar um admin inicial se não existir
        initial_admin_username = os.getenv('INITIAL_ADMIN_USERNAME', 'admin')
        initial_admin_password = os.getenv('INITIAL_ADMIN_PASSWORD', 'admin123')

        if not User.query.filter_by(username=initial_admin_username).first():
            hashed_password = generate_password_hash(initial_admin_password, method='pbkdf2:sha256')
            admin_user = User(username=initial_admin_username, password_hash=hashed_password)
            db.session.add(admin_user)
            db.session.commit()
            print(f"Usuário '{initial_admin_username}' criado com a senha inicial.")
    app.run(debug=True)