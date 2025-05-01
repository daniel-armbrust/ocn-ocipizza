#
# api/app/modules/pizza.py
#

from app.modules.nosql import NoSQL


class Pizza():
    def __init__(self):        
        self.__nosql = NoSQL()        
        
    def list(self):
        sql = f'''
            SELECT id, name, description, price, image
                FROM pizza
        '''

        data = self.__nosql.query(sql)

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