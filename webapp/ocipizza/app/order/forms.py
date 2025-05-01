#
# app/order/forms.py
#

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, HiddenField, validators

class OrderAddressDeliveryForm(FlaskForm):
    zipcode = StringField('CEP', [ 
        validators.Length(min=8, max=10, message=u'Invalid delivery zipcode'),    
        validators.DataRequired()
    ])

    address = StringField('Endereço', [ 
        validators.Length(min=2, max=150, message=u'Invalid delivery address'),
        validators.DataRequired()
    ])

    address_number = IntegerField('Número', [ 
        validators.NumberRange(min=1, message=u'Invalid delivery address number'),
        validators.DataRequired()
    ])

    address_neighborhood = StringField('Bairro', [ 
        validators.Length(min=2, max=150, message=u'Invalid delivery address neighborhood'),
        validators.DataRequired()
    ])

    address_complement = StringField('Complemento', [ 
        validators.Length(min=2, max=200, message=u'Invalid delivery address complement'),
        validators.Optional()       
    ])

    address_refpoint = StringField('Ponto de referência', [ 
        validators.Length(min=2, max=100, message=u'Invalid delivery address reference point'),
        validators.Optional()
    ])