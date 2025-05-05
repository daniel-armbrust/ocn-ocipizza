#
# fn-user-registry-email/func.py
#

import io
import json

from fdk import response

from modules.user import User
from modules.email import Email

def handler(ctx, data: io.BytesIO = None):
    """Esta função recebe os dados para o registro de um novo usuário. Após a 
    inserção dos dados no banco de dados, um e-mail será enviado ao usuário 
    para confirmar seu endereço de e-mail e ativar seu cadastro.

    Exemplo do payload que deve ser recebido para processamento:

       {"email": "darmbrust@gmail.com", "password": "S3cr3t0",
        "name": "Daniel Armbrust", "telephone": "(99) 9999-9999"}

    """
    try:      
        bin_data = data.getvalue()
        decoded_data = bin_data.decode('utf-8')
        body = json.loads(decoded_data.replace("'", '"'))

        user_name = body['name']        
        email_address = body['email']        
        user_telephone = body['telephone']                
    except Exception as ex:       
        error = f'Error parsing json payload: {ex}'
        raise Exception(error)
    
    resp = {}
        
    user = User()   
    
    user_exists = user.exists(
        email=email_address, 
        telephone=user_telephone
    )  

    if not user_exists:
        added = user.add(data=body)
        user.close()

        if added:
            email = Email()
            email.address = email_address      
            email.name = user_name      
            email.send()

            resp = {'status': 'success', 
                    'message': 'E-mail sent successfully.',
                    'data': {
                        'name': user_name,
                        'email': email_address
                   }}
        else:
            resp = {'status': 'fail', 
                    'message': 'The email was not sent.',
                    'data': {
                        'name': user_name,
                        'email': email_address
                   }}
    else:
        resp = {'status': 'fail', 
                'message': 'User already exists.',
                'data': {
                    'name': user_name,
                    'email': email_address
               }}
        
    return response.Response(
        ctx, response_data=json.dumps(resp),
        headers={'Content-Type': 'application/json'}
    )
