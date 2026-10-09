#
# form/user_forms.py
#


from wtforms import EmailField, Form, PasswordField, StringField, ValidationError
from wtforms.validators import DataRequired, Email, Length, Regexp

from app.utils.utils import normalize_whatsapp


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


class UserRegisterForm(Form):
    """
    Define, renderiza e valida os campos do cadastro de usuário.
    """

    full_name = StringField(
        'Nome completo',
        validators=[
            DataRequired(message='Informe seu nome completo.'),
            Length(
                min=3,
                max=255,
                message='O nome deve conter entre 3 e 255 caracteres.'
            )
        ],
        render_kw={
            'type': 'text',
            'minlength': 3,
            'maxlength': 255,
            'autocomplete': 'name',
            'required': True
        }
    )

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

    whatsapp = StringField(
        'WhatsApp',
        filters=[normalize_whatsapp],
        validators=[
            DataRequired(message='Informe seu WhatsApp.'),
            Regexp(
                r'^\d{11}$',
                message='Informe um WhatsApp no formato (99) 99999-9999.'
            )
        ],
        render_kw={
            'type': 'tel',
            'minlength': 15,
            'maxlength': 15,
            'pattern': r'\([0-9]{2}\) [0-9]{5}-[0-9]{4}',
            'inputmode': 'numeric',
            'autocomplete': 'tel',
            'aria-describedby': 'whatsapp-help',
            'data-whatsapp-mask': True,
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
            'autocomplete': 'new-password',
            'aria-describedby': 'password-help',
            'required': True
        }
    )

    def validate_full_name(self, field: StringField) -> None:
        """
        Verifica se o usuário informou nome e sobrenome.

        Args:
            field: Campo do nome completo já processado pelo WTForms.

        Returns:
            Nada. O valor normalizado é armazenado no próprio campo.

        Raises:
            ValidationError: Caso o nome não contenha ao menos duas partes.
        """

        field.data = ' '.join(field.data.split())

        if len(field.data.split()) < 2:
            raise ValidationError('Informe o nome completo.')