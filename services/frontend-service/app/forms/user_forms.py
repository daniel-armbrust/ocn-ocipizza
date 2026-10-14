#
# forms/user_forms.py
#

from wtforms import BooleanField, EmailField, Form, StringField
from wtforms.validators import (
    AnyOf,
    DataRequired,
    Email,
    Length,
    Optional,
    Regexp
)

from app.utils.utils import (
    normalize_optional_string,
    normalize_state,
    normalize_whatsapp,
    normalize_zip_code
)


class UserPasswordResetRequestForm(Form):
    """
    Define e valida o campo utilizado para solicitar a redefinição de senha.
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


class UserWhatsappUpdateForm(Form):
    """
    Define, renderiza e valida o campo de atualização do WhatsApp.
    """

    whatsapp = StringField(
        'WhatsApp',
        filters=[normalize_whatsapp],
        validators=[
            DataRequired(message='Informe seu WhatsApp.'),
            Regexp(
                r'^\d{11}$',
                message='Informe um WhatsApp no formato 99 99999 9999.'
            )
        ],
        render_kw={
            'type': 'tel',
            'minlength': 15,
            'maxlength': 15,
            'pattern': r'\([0-9]{2}\) [0-9]{5}-[0-9]{4}',
            'inputmode': 'numeric',
            'autocomplete': 'tel',
            'data-whatsapp-mask': True,
            'data-profile-whatsapp': True,
            'required': True
        }
    )


class UserAddressForm(Form):
    """
    Define, renderiza e valida os campos do endereço do usuário.
    """

    label = StringField(
        'Identificação do endereço',
        filters=[normalize_optional_string],
        validators=[
            Optional(),
            Length(
                max=50,
                message='A identificação deve conter no máximo 50 caracteres.'
            )
        ],
        render_kw={
            'maxlength': 50,
            'autocomplete': 'off',
            'placeholder': 'Ex.: Casa, trabalho'
        }
    )

    zip_code = StringField(
        'CEP',
        filters=[normalize_zip_code],
        validators=[
            DataRequired(message='Informe o CEP.'),
            Regexp(
                r'^\d{8}$',
                message='Informe um CEP válido.'
            )
        ],
        render_kw={
            'minlength': 8,
            'maxlength': 9,
            'pattern': r'[0-9]{5}-[0-9]{3}',
            'inputmode': 'numeric',
            'autocomplete': 'postal-code',
            'data-zip-code-mask': True,
            'required': True
        }
    )

    street = StringField(
        'Logradouro',
        validators=[
            DataRequired(message='Informe o logradouro.'),
            Length(
                max=255,
                message='O logradouro deve conter no máximo 255 caracteres.'
            )
        ],
        render_kw={
            'maxlength': 255,
            'autocomplete': 'address-line1',
            'required': True
        }
    )

    number = StringField(
        'Número',
        validators=[
            DataRequired(message='Informe o número.'),
            Regexp(
                r'^\d+$',
                message='O número do endereço deve conter somente números.'
            ),
            Length(
                max=20,
                message='O número deve conter no máximo 20 dígitos.'
            )
        ],
        render_kw={
            'maxlength': 20,
            'pattern': r'[0-9]+',
            'inputmode': 'numeric',
            'autocomplete': 'address-line2',
            'data-numeric-only': True,
            'required': True
        }
    )

    complement = StringField(
        'Complemento',
        filters=[normalize_optional_string],
        validators=[
            Optional(),
            Length(
                max=100,
                message='O complemento deve conter no máximo 100 caracteres.'
            )
        ],
        render_kw={
            'maxlength': 100,
            'autocomplete': 'address-line3'
        }
    )

    neighborhood = StringField(
        'Bairro',
        validators=[
            DataRequired(message='Informe o bairro.'),
            Length(
                max=100,
                message='O bairro deve conter no máximo 100 caracteres.'
            )
        ],
        render_kw={
            'maxlength': 100,
            'required': True
        }
    )

    city = StringField(
        'Cidade',
        default='Sorocaba',
        validators=[
            DataRequired(message='Informe a cidade.'),
            AnyOf(
                ['Sorocaba'],
                message='A cidade atendida deve ser Sorocaba.'
            )
        ],
        render_kw={
            'autocomplete': 'address-level2',
            'readonly': True,
            'required': True
        }
    )

    state = StringField(
        'Estado',
        default='SP',
        filters=[normalize_state],
        validators=[
            DataRequired(message='Informe o estado.'),
            AnyOf(
                ['SP'],
                message='O estado atendido deve ser SP.'
            )
        ],
        render_kw={
            'autocomplete': 'address-level1',
            'readonly': True,
            'required': True
        }
    )

    is_default = BooleanField(
        'Usar como endereço principal',
        default=False,
        render_kw={
            'value': 'true'
        }
    )
