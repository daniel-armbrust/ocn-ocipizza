#
# forms/user_forms.py
#


from wtforms import (
    EmailField,
    Form,
    PasswordField
)

from wtforms.validators import DataRequired, Email, Length, Regexp


class UserLoginForm(Form):
    """
    Define, renderiza e valida os campos de autenticação do usuário.
    """

    email = EmailField(
        'E-mail',
        validators=[
            DataRequired(message='Informe seu e-mail.'),
            Email(message='Informe um endereço de e-mail válido.')
        ],
        render_kw={
            'autocomplete': 'email',
            'required': True
        }
    )

    password = PasswordField(
        'Senha',
        validators=[
            DataRequired(message='Informe sua senha.'),
            Length(
                min=8,
                max=20,
                message='A senha deve conter entre 8 e 20 caracteres.'
            )
        ],
        render_kw={
            'minlength': 8,
            'maxlength': 20,
            'autocomplete': 'current-password',
            'required': True
        }
    )