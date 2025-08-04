from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Aluno(db.Model):
    __tablename__ = 'alunos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)  # Alterado de email para cpf
    telefone = db.Column(db.String(20))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    # pagamentos terá um cascade para deletar pagamentos quando um aluno é excluído
    pagamentos = db.relationship('Pagamento', backref='aluno', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Aluno {self.nome} {self.sobrenome}>'

class Pagamento(db.Model):
    __tablename__ = 'pagamentos'
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data_pagamento = db.Column(db.DateTime, default=datetime.utcnow)
    data_vencimento = db.Column(db.Date) # Apenas a data
    status = db.Column(db.String(50), default='Pendente') # Ex: 'Pago', 'Pendente', 'Atrasado'
    descricao = db.Column(db.String(200))

    def __repr__(self):
        return f'<Pagamento {self.valor} para Aluno {self.aluno_id}>'

# Este é o HOOK que o app.py usará para inicializar db e login_manager
def init_app_models(app_instance, db_instance, login_manager_instance):
    db_instance.init_app(app_instance)
    login_manager_instance.init_app(app_instance)

    @login_manager_instance.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))