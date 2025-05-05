#
# fn-password-recovery-email/func.py
#

import io
import json

from fdk import response

from modules.user import User

def handler(ctx, data: io.BytesIO = None):
    """Esta função recebe o endereço de e-mail do usuário e, em seguida, 
    envia um e-mail para a recuperação da senha.
    
    Exemplo do payload que deve ser recebido para processamento:

       {"email": "darmbrust@gmail.com"}

    """   
    try:
        bin_data = data.getvalue()
        decoded_data = bin_data.decode('utf-8')
        body = json.loads(decoded_data.replace("'", '"'))        

        email_address = body['email'] 
    except (Exception, ValueError) as ex:
        error = f'Error parsing json payload: {ex}'
        raise Exception(error)
    
    resp = {}

    user = User()      
    user.email = email_address
    status = user.password_recovery()

    if status is True:
        resp = {'status': 'success', 
                'message': 'E-mail for password recovery sent successfully.',
                'data': {'email': email_address}}
    else:
        resp = {'status': 'fail', 
                'message': 'E-mail for password recovery was not sent.',
                'data': {'email': email_address}}
      
    return response.Response(
        ctx, response_data=json.dumps(resp),
        headers={"Content-Type": "application/json"}
    )
