#
# fn-password-recovery-email/modules/user.py
#

from . import utils
from .nosql import NoSQL
from .email import Email

class User():       
    @property
    def email(self):
        return self.__email
    
    @email.setter
    def email(self, value: str):
        self.__email = value

    def __init__(self):
        self.__nosql = NoSQL()
    
    def __exists(self):
        """Verifica se o usuário existe através do e-mail informado."""

        sql = f'''
            SELECT email FROM user WHERE email = "{self.__email}" LIMIT 1
        '''

        result = self.__nosql.query(sql)        

        if result:
            if result[0]['email'] == self.__email:
                return True
        
        return False
    
    def __update_recv_info(self, data: dict):
        """Atualiza os dados de recuperação de senha."""

        sql = f'''
            UPDATE email_verification 
                SET token = "{data['token']}", 
                    expiration_ts = "{data['expiration_ts']}",
                    password_recovery = True
            WHERE email = "{data['email']}"
        '''

        result = self.__nosql.query(sql)        

        if result:
            if result[0]['NumRowsUpdated'] == 1:
                return True
            
        return False

    def __add_recv_info(self, data: dict):
        status = False

        for i in range(2): 
            status = self.__nosql.add(data)            
        
            if status is True:                
                break
            else:
                status = self.__update_recv_info(data)                
        
        self.__nosql.close()
        
        return status

    def password_recovery(self):
        user_exists = self.__exists()        

        if user_exists:
            data = {}

            token = utils.get_token()
            expiration_ts = utils.get_expiration_ts()
            
            data['email'] = self.__email
            data['token'] = token
            data['expiration_ts'] = expiration_ts
            data['password_recovery'] = True

            added = self.__add_recv_info(data=data)

            if added:
                email = Email()
                email.address = self.__email
                email.token = token
                email_sent = email.send()

                if email_sent:
                    return True                
        
        return False