from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DecimalField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=2, max=80)])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class AlunoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    sobrenome = StringField('Sobrenome', validators=[DataRequired(), Length(max=100)])
    telefone = StringField('Telefone', validators=[Optional(), Length(max=20)])
    cpf = StringField('CPF', validators=[DataRequired(), Length(min=11, max=14)])  # Novo campo
    submit = SubmitField('Salvar Aluno')

class PagamentoForm(FlaskForm):
    valor = DecimalField('Valor', validators=[DataRequired()])
    data_vencimento = DateField('Data de Vencimento (AAAA-MM-DD)', format='%Y-%m-%d', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Pago', 'Pago'), ('Pendente', 'Pendente'), ('Atrasado', 'Atrasado')], validators=[DataRequired()])
    descricao = TextAreaField('Descrição', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Registrar Pagamento')