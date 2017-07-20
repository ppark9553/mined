import os, sys
parent_dir = os.path.dirname(os.getcwd())
sys.path.insert(0, parent_dir)

from Gobble.pdreader import PDReader

import datetime
import simplejson as json
import pandas as pd
import pandas_datareader.data as web
import pymysql

class Safer:

    def __init__(self, start, end):
        self.pr = PDReader(start, end)

    def connect_to_db(self):
        self.conn = pymysql.connect(host="45.55.86.183", port=3306, user="minestoned", \
            passwd="moneyisnoweverythingdawg", db="stock")

    def create_prep_data_table(self):
        cursor = self.conn.cursor()
        table_exists = cursor.execute("SHOW TABLES LIKE 'prep';")
        if table_exists == 0:
            cursor.execute("CREATE TABLE prep (prepData text, prepValue text);")

    def prep_home_data(self):
        json_data = dict()

        kp = self.pr.request_df("KOSPI")[["date", "close", "volume"]]
        kp = kp.set_index(pd.to_datetime(kp.date.astype("str")))
        kp = kp.resample('M').apply({'close': 'last', 'volume': 'sum'})

        kp_c = kp['close'][-24:] # 2 years
        date = [str(date) for date in kp_c.index.strftime('%Y%m')]
        kp_c = list(kp_c)
        price_data = '['
        for i in range(len(date)):
        	data_dict = '{ Period: ' + date[i] + ', Price: ' + str(int(kp_c[i])) + ' }'
        	if i != len(date)-1:
        		data_dict += ', '
        	price_data += data_dict
        price_data += ']'
        json_data["price"] = price_data

        kp_v = kp['volume'][-24:]
        kp_v = list(kp_v)
        volume_data = '['
        for i in range(len(date)):
        	data_dict = '{ Period: ' + date[i] + ', Volume: ' + str(kp_v[i]) + ' }'
        	if i != len(date)-1:
        		data_dict += ', '
        	volume_data += data_dict
        volume_data += ']'
        json_data["volume"] = volume_data

        with open("./json/home.json", "w") as f:
            json.dump(json_data, f)

    def update_prep_db(self, json_file):
        with open("./json/" + json_file) as f:
            json_data = json.load(f)
        cursor = self.conn.cursor()
        for key, val in json_data.items():
            cursor.execute("INSERT INTO prep (prepData, prepValue) VALUES ('{}', '{}');".format(key, val))
        self.conn.commit()

s = Safer("20100101", "20170717")
s.connect_to_db()
s.create_prep_data_table()
s.update_prep_db("home.json")
