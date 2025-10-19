#
# api/app/modules/pizza.py
#

from app.modules.nosql import NoSQL
from app.settings import Settings

class Pizza():
    def __init__(self):        
        self.__nosql = NoSQL()        
        
    def list(self):
        settings = Settings()

        sql = f'''
            SELECT id, name, description, price, image
                FROM pizza
        '''

        data = self.__nosql.query(sql)

        # Substitui o nome da imagem pela URL completa do Object Storage da 
        # região correspondente.
        i = 0
        while i < len(data):
            image_filename = data[i]['image']
            image_url = f'https://objectstorage.{settings.oci_region}.oraclecloud.com/n/{settings.oci_objs_namespace}/b/pizza/o/{image_filename}'
            
            data[i]['image'] = image_url
            i += 1

        return data

    def get(self, id: int):
        sql = f'''
            SELECT id, name, description, price, image
                FROM pizza
            WHERE id = {id}
        '''

        resp = self.__nosql.query(sql)
        
        try:
            data = resp[0]
        except (IndexError, KeyError,):
            return None
        else:
            return data
    
    def exist(self, id: int):
        data = self.get(id)

        if data[0] == id:
            return True
        else:
            return False  