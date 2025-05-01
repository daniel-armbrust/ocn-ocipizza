#
# app/user/user.py
#

from flask_login import UserMixin, login_manager
from werkzeug.security import check_password_hash

from app.modules.nosql import NoSQL
from app.modules.utils import extract_digits

class MyUserMixin(UserMixin):
    def __init__(self, id):
        self.id = id

class User():
    def __init__(self):                    
        self.__nosql = NoSQL()
        
    def get_id(self, email: str):
        sql = f'''
            SELECT id 
                FROM user 
            WHERE
                email = "{email}"
        '''

        result = self.__nosql.query(sql)      

        if result:          
            return result[0]['id']
        else:
            return None
    
    def check_password(self, email: str, password: str): 
        sql = f'''
            SELECT email, password, verified 
                FROM user 
            WHERE 
                email = "{email}"
        '''

        data = self.__nosql.query(sql)        

        if data and (data[0]['email'] == email and data[0]['verified'] is True):
            stored_password_hash = data[0]['password']
                       
            if check_password_hash(stored_password_hash, password):               
                return True
            
        return False

    def check_email(self, email: str):
        sql = f'''
            SELECT email 
                FROM user
            WHERE
                email = "{email}"
        '''
        data = self.__nosql.query(sql)

        if data and (data[0]['email'] == email):
            return True
        else:
            return False
    
    def exists(self, email: str, telephone: str):
        """Verifica se o usuário existe através do email e telefone."""

        # Mantém somente os digitos numéricos do telefone. 
        telephone_num = extract_digits(telephone)

        sql = f'''
            SELECT email, telephone 
                FROM user
            WHERE
                email = "{email}" OR telephone = "{telephone_num}"
        '''

        result = self.__nosql.query(sql)

        if result:
            if result[0]['email'] == email or result[0]['telephone'] == telephone_num:
                return True
        
        return False

    def activate(self, email: str, token: str):
        """Ativa e confirma a conta do usuário."""

        sql_select = f'''
            SELECT email, token, expiration_ts 
                FROM email_verification
            WHERE (email = "{email}" AND token = "{token}") 
                AND password_recovery = False
        '''
        result = self.__nosql.query(sql_select)

        if result:            
            if result[0]['email'] == email and result[0]['token'] == token:
                # TODO: verificar "expiration_ts"
                user_id = self.get_id(email=email)

                sql_update = f'''
                    UPDATE user SET verified = True WHERE id = {user_id}
                '''
                                
                result = self.__nosql.query(sql_update)

                if result and result[0]['NumRowsUpdated'] == 1:
                    sql_delete = f'''
                        DELETE 
                            FROM email_verification
                        WHERE email = "{email}" AND token = "{token}"
                    '''

                    self.__nosql.query(sql_delete)

                    return True
                
        return False    