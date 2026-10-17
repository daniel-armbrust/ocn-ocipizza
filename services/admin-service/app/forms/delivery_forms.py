#
# forms/delivery_forms.py
#

from wtforms import (
    BooleanField, 
    DecimalField, 
    Form, 
    IntegerField, 
    StringField
)

from wtforms.validators import (
    DataRequired, 
    NumberRange, 
    Optional, 
    Regexp
)


class DeliveryAreaForm(Form):
    """
    Valida os dados de criação de uma área de entrega.
    """

    name = StringField(
        validators=[
            DataRequired(), 
            Regexp(r'^.{1,100}$')
        ]
    )

    zip_code_start = StringField(
        validators=[
            DataRequired(), 
            Regexp(r'^\d{5}-?\d{3}$')
        ]
    )

    zip_code_end = StringField(
        validators=[
            DataRequired(), 
            Regexp(r'^\d{5}-?\d{3}$')
        ]
    )

    delivery_fee = DecimalField(
        validators=[
            DataRequired(), 
            NumberRange(min=0)
        ]
    )

    estimated_minutes = IntegerField(
        validators=[
            DataRequired(), 
            NumberRange(min=1)
        ]
    )
    
    active = BooleanField(default=True)


class DeliveryAreaUpdateForm(DeliveryAreaForm):
    """
    Valida os dados de edição de uma área de entrega.
    """

    name = StringField(
        validators=[
            Optional(), 
            Regexp(r'^.{1,100}$')
        ]
    )

    zip_code_start = StringField(
        validators=[
            Optional(), 
            Regexp(r'^\d{5}-?\d{3}$')
        ]
    )

    zip_code_end = StringField(
        validators=[
            Optional(), 
            Regexp(r'^\d{5}-?\d{3}$')\
        ]
    )

    delivery_fee = DecimalField(
        validators=[
            Optional(), 
            NumberRange(min=0)
        ]
    )

    estimated_minutes = IntegerField(
        validators=[
            Optional(), 
            NumberRange(min=1)
        ]
    )


class DeliveryAreaDeleteForm(Form):
    """
    Representa o formulário de confirmação de exclusão.
    """
    pass


class DeliveryAreaActiveForm(Form):
    """
    Valida a alteração do estado de uma área de entrega.
    """
    active = BooleanField(default=False)