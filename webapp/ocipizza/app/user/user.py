#
# app/user/user.py
#

from datetime import datetime

from flask_login import UserMixin, login_manager
from werkzeug.security import check_password_hash, generate_password_hash

from app.modules.nosql import NoSQL
from app.modules.functions import Functions
from app.modules.utils import extract_digits

from app.settings import Settings

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
            LIMIT 1
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
            LIMIT 1
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
            LIMIT 1
        '''
        data = self.__nosql.query(sql)

        if data and (data[0]['email'] == email):
            return True
        else:
            return False
    
    def exists(self, email: str, telephone: str):
        """
        Verifica se o usuário existe através do email e telefone.
        """

        # Mantém somente os digitos numéricos do telefone. 
        telephone_num = extract_digits(telephone)

        sql = f'''
            SELECT email, telephone 
                FROM user
            WHERE
                email = "{email}" OR telephone = "{telephone_num}"
            LIMIT 1
        '''

        result = self.__nosql.query(sql)
       
        if result:
            if result[0]['email'] == email or result[0]['telephone'] == telephone_num:
                return True
        
        return False


class UserRegister():
    """
    Classe responsável pelas funcionalidades de registro de novos usuários.
    """

    def __init__(self):
        self.__settings = Settings()
        self.__fn = Functions()
        self.__nosql = NoSQL()

        if self.__settings.env == 'development':            
            self.__fn.fn_endpoint = self.__settings.fn_user_register_endpoint 
        else:
            self.__fn.fn_ocid = self.__settings.fn_user_register_ocid

    def add(self, user_data: dict):
        """Adiciona um novo usuário, mas com o status desativado."""
        invoke_status = self.__fn.invoke(json_message=user_data)

        return invoke_status
    
    def activate(self, email: str, token: str):
        """Ativa e confirma a conta do usuário."""

        user = User()

        sql_select = f'''
            SELECT email, token, expiration_ts 
                FROM email_verification
            WHERE (email = "{email}" AND token = "{token}") 
                AND password_recovery = False 
            LIMIT 1
        '''
        result = self.__nosql.query(sql_select)

        if result:            
            if result[0]['email'] == email and result[0]['token'] == token:
                # TODO: verificar "expiration_ts"
                user_id = user.get_id(email=email)

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


class UserPassword():
    @property
    def user_id(self):
        return self.__user_id
    
    @user_id.setter
    def user_id(self, value: int):
        self.__user_id = value

    @property
    def email(self):
        return self.__email
    
    @email.setter
    def email(self, value: str):
        self.__email = value
    
    @property
    def token(self):
        return self.__token
    
    @token.setter
    def token(self, value: str):
        self.__token = value
    
    @property
    def password(self):
        return self.__password
    
    @password.setter
    def password(self, value: str):
        self.__password = value

    def __init__(self):        
        self.__settings = Settings()
        self.__fn = Functions()
        self.__nosql = NoSQL()

        if self.__settings.env == 'development':
            self.__fn.fn_endpoint = self.__settings.fn_password_recovery_endpoint 
        else:
            self.__fn.fn_ocid = self.__settings.fn_user_register_ocid
    
    def __check_token(self):
        sql = f'''
            SELECT email, token, expiration_ts 
                FROM email_verification
            WHERE email = "{self.__email}" AND token = "{self.__token}"
            LIMIT 1          
        '''

        result = self.__nosql.query(sql)       

        if result:            
            if result[0]['email'] == self.__email and result[0]['token'] == self.__token:                
                expiration_ts = result[0]['expiration_ts']
                current_ts = int(datetime.now().timestamp())

                if current_ts <= expiration_ts:
                    return True
            
        return False
    
    def __update(self, hash_password: str):
        sql_update = f'''
            UPDATE user SET password = "{hash_password}", verified = True 
                WHERE id = {self.__user_id}
        '''
        
        result = self.__nosql.query(sql_update)       

        if result and result[0]['NumRowsUpdated'] == 1:            
            sql_delete = f'''
                DELETE FROM email_verification 
                    WHERE email = "{self.__email}" AND token = "{self.__token}"
                LIMIT 1
            '''

            self.__nosql.query(sql_delete)

            return True
        
        return False

    def recovery(self, json_message: dict):
        invoke_status = self.__fn.invoke(json_message=json_message)

        return invoke_status
    
    def set(self):
        token_valid = self.__check_token()  

        if token_valid:    
            hashed_password = generate_password_hash(method='pbkdf2', password=self.__password)

            password_update = self.__update(hashed_password)

            if password_update is True:
                return True

        return False