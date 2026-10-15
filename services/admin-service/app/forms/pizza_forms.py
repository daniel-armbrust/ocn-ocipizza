#
# forms/pizza_forms.py
#

from wtforms import (
    BooleanField,
    DecimalField,
    FileField,
    Form,
    SelectField,
    StringField
)

from wtforms.validators import DataRequired, Optional, Length, NumberRange


class PizzaForm(Form):
    """
    Define e valida os campos do formulário de criação de uma pizza.
    """

    name = StringField(
        validators=[
            DataRequired(), 
            Length(max=100)
        ]
    )

    description = StringField(
        validators=[
            DataRequired(), 
            Length(max=500)
        ]
    )
    
    category = SelectField(
        choices=[
            ('salgada', 'Salgada'),
            ('vegetariana', 'Vegetariana'),
            ('doce', 'Doce')
        ],
        validators=[DataRequired()]
    )
    
    price = DecimalField(
        validators=[
            DataRequired(), 
            NumberRange(min=0.01)
        ]
    )
    
    image = FileField(
        validators=[
            DataRequired()
        ]
    )
    
    available = BooleanField(default=True)


class PizzaUpdateForm(PizzaForm):
    """
    Define e valida os campos opcionais de edição de uma pizza.
    """

    name = StringField(
        validators=[
            Optional(), 
            Length(max=100)
        ]
    )
    
    description = StringField(
        validators=[
            Optional(), 
            Length(max=500)
        ]
    )
    
    category = SelectField(
        choices=[
            ('', 'Manter categoria'),
            ('salgada', 'Salgada'),
            ('vegetariana', 'Vegetariana'),
            ('doce', 'Doce')
        ],
        validators=[Optional()]
    )
    
    price = DecimalField(
        validators=[
            Optional(), 
            NumberRange(min=0.01)
        ]
    )
    
    image = FileField(
        validators=[
            Optional()
        ]
    )
    
    available = BooleanField()


class PizzaDeleteForm(Form):
    """
    Representa o formulário de confirmação da exclusão de uma pizza.
    """
    pass
