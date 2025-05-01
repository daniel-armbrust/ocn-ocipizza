#
# app/user/password.py
#

from datetime import datetime

from werkzeug.security import generate_password_hash

from app.modules.nosql import NoSQL

class Password():
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
        self.__nosql = NoSQL()
    
    def __check_token(self):
        sql = f'''
            SELECT email, token, expiration_ts 
                FROM email_verification
            WHERE email = "{self.__email}" AND token = "{self.__token}"            
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
            '''

            self.__nosql.query(sql_delete)

            return True
        
        return False

    def set(self):
        token_valid = self.__check_token()  

        if token_valid:    
            hashed_password = generate_password_hash(self.__password)

            password_update = self.__update(hashed_password)

            if password_update is True:
                return True

        return False    