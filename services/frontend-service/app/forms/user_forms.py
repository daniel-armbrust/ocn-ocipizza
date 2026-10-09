#
# forms/user_forms.py
#

from wtforms import BooleanField, Form, StringField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from app.utils.utils import (
    normalize_optional_string,
    normalize_state,
    normalize_whatsapp
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
        validators=[
            DataRequired(message='Informe o CEP.'),
            Regexp(
                r'^\d{5}-?\d{3}$',
                message='Informe um CEP válido.'
            )
        ],
        render_kw={
            'minlength': 8,
            'maxlength': 9,
            'inputmode': 'numeric',
            'autocomplete': 'postal-code',
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
            Length(
                max=20,
                message='O número deve conter no máximo 20 caracteres.'
            )
        ],
        render_kw={
            'maxlength': 20,
            'autocomplete': 'address-line2',
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
        validators=[
            DataRequired(message='Informe a cidade.'),
            Length(
                max=100,
                message='A cidade deve conter no máximo 100 caracteres.'
            )
        ],
        render_kw={
            'maxlength': 100,
            'autocomplete': 'address-level2',
            'required': True
        }
    )

    state = StringField(
        'Estado',
        filters=[normalize_state],
        validators=[
            DataRequired(message='Informe o estado.'),
            Regexp(
                r'^[A-Z]{2}$',
                message='Informe a sigla do estado com duas letras.'
            )
        ],
        render_kw={
            'minlength': 2,
            'maxlength': 2,
            'autocomplete': 'address-level1',
            'autocapitalize': 'characters',
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
