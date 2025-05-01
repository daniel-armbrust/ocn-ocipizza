#
# app/user/forms.py
#

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators

class LoginForm(FlaskForm):    
    email = StringField('Email', [
        validators.Email(message=(u'Endereço de e-mail inválido.')),
        validators.DataRequired()
    ])

    password = PasswordField('Senha', [
        validators.Length(min=10, max=50, message=u'Senha inválida.'),
        validators.DataRequired()
    ])


class NewUserForm(FlaskForm):
    email = StringField('Email', [
        validators.Email(message=(u'Endereço de e-mail inválido.')),
        validators.DataRequired()
    ])

    password = PasswordField('Senha', [
        validators.Length(min=10, max=30, message=u'Senha inválida.'),        
        validators.DataRequired()
    ])    

    name = StringField('Nome', [ 
        validators.Length(min=2, max=200, message=u'Nome inválido.'),
        validators.DataRequired()
    ])

    telephone = StringField('Telefone / WhatsApp', [ 
        validators.Length(min=10, max=15, message=u'Numero de telefone inválido.'),
        validators.Regexp(regex='^[0-9\(\)\-\ \+]+$'),
        validators.DataRequired()
    ])


class PasswordRecoveryForm(FlaskForm):
    email = StringField('Email', [
        validators.Email(message=(u'Endereço de e-mail inválido.')),
        validators.DataRequired()
    ])


class NewPasswordForm(FlaskForm):
    password = PasswordField('Senha', [
        validators.Length(min=10, max=50, message=u'Senha inválida.'),
        validators.DataRequired()
    ])

    confirm_password = PasswordField('Confirme a Senha', [        
        validators.DataRequired(),
        validators.EqualTo('password', message='As senhas devem corresponder.')
    ])