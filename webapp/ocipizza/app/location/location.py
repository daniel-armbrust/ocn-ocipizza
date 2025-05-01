#
# app/location/location.py
#

import sqlite3

class Zipcode():
    def get_state_city(self, zipcode: str):
        conn = sqlite3.connect('app/location/zipcode.db')
        cursor = conn.cursor()

        sql = f'''
            SELECT state, city FROM zipcode 
                WHERE start <= '{zipcode}' AND end >= '{zipcode}'
            LIMIT 1;
        '''

        cursor.execute(sql)

        state = ''
        city = ''

        try:
            (state, city,) = cursor.fetchone()
        except TypeError:
            return (None, None,)
        else:
            return (state, city,)