#
# app/order/order.py
#
from decimal import Decimal
from datetime import datetime

from app.settings import Settings
from app.modules.nosql import NoSQL
from app.pizza.pizza import Pizza

class Order():
    def __init__(self):
        self.__settings = Settings()
        self.__nosql = NoSQL()
    
    def add(self, data: dict):
        """Add a new pizza order.
        
        """
        total = 0
        pizza_list = []

        pizza = Pizza()      

        for pizza_id in data['pizza_id_list']:
            pizza_data = pizza.get(pizza_id)

            try:
                pizza_list.append({'pizza': pizza_data['name'], 
                                   'price': pizza_data['price']})
            except TypeError:
                return False
            
            total += Decimal(pizza_data['price'])
                        
        data.pop('pizza_id_list')

        data['pizza'] = pizza_list
        data['total'] = float(total)
        data['order_datetime'] = datetime.now()

        try:
            data['address'] = {'zipcode': data.pop('zipcode'), 
                               'address': data.pop('address'),
                               'address_number': data.pop('address_number'),
                               'address_neighborhood': data.pop('address_neighborhood'),
                               'address_complement': data.pop('address_complement'),
                               'address_refpoint': data.pop('address_refpoint')}
        except KeyError:
            return False

        added = self.__nosql.save(
            table_name=self.__settings.nosql_order_table_name, 
            data=data)
        
        # TODO: log errors
        if added:
            return True
        
        return False
    
    def list(self, user_id: int):
        sql = f'''
            SELECT order_id, address, pizza, total, order_datetime, status
                FROM user.order
            WHERE id = {user_id}
        '''

        data_list = self.__nosql.query(sql) 
             
        datetime_format = '%Y-%m-%dT%H:%M:%SZ'     

        i = 0
        while i < len(data_list):
            data = data_list[i]

            order_datetime = data['order_datetime']
            datetime_obj = datetime.strptime(order_datetime, datetime_format)

            data['order_datetime'] = \
                f'{datetime_obj.day}/{datetime_obj.month}/{datetime_obj.year} ' + \
                f'{datetime_obj.hour}:{datetime_obj.minute}'
            
            data_list[i] = data
            i += 1

        return data_list