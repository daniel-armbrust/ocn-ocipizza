#
# forms/user_forms.py
#

from wtforms import (
    BooleanField,
    EmailField,
    Form,
    PasswordField,
    RadioField,
    StringField
)

from wtforms.validators import DataRequired, Email, Length


class UserCreateForm(Form):
    """
    Define e valida os dados necessários para criar um usuário.
    """

    full_name = StringField(
        validators=[
            DataRequired(message='Informe o nome completo.'),
            Length(min=3, max=255)
        ]
    )

    email = EmailField(
        validators=[
            DataRequired(message='Informe o e-mail.'),
            Email(message='Informe um e-mail válido.')
        ]
    )
    
    whatsapp = StringField(
        validators=[
            DataRequired(message='Informe o WhatsApp.'),
            Length(min=11, max=15)
        ]
    )
    
    password = PasswordField(
        validators=[
            DataRequired(message='Informe a senha.'),
            Length(min=8, max=20)
        ]
    )
    
    role = RadioField(
        choices=[
            ('regular', 'Usuário regular'),
            ('kitchen', 'Cozinha'),
            ('admin', 'Administrador')
        ],
        validators=[DataRequired(message='Selecione um perfil.')]
    )

    confirmed = BooleanField(default=False)

class UserUpdateForm(Form):
    """
    Define e valida os dados administrativos de atualização do usuário.
    """

    full_name = StringField(
        validators=[
            DataRequired(message='Informe o nome completo.'),
            Length(min=3, max=255)
        ]
    )
    
    email = EmailField(
        validators=[
            DataRequired(message='Informe o e-mail.'),
            Email(message='Informe um e-mail válido.')
        ]
    )
    
    whatsapp = StringField(
        validators=[
            DataRequired(message='Informe o WhatsApp.'),
            Length(min=11, max=15)
        ]
    )
    
    role = RadioField(
        choices=[
            ('regular', 'Usuário regular'),
            ('kitchen', 'Cozinha'),
            ('admin', 'Administrador')
        ],
        validators=[DataRequired(message='Selecione um perfil.')]
    )
    
    confirmed = BooleanField(default=False)


class UserDeleteForm(Form):
    """
    Representa o formulário de confirmação da exclusão de um usuário.
    """
    pass
