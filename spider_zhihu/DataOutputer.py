# coding:utf8

import sqlite3

class DataOutputer(object):

    # def __init__(self):
    #     self.datas = []

    # def collect_data(self, data):
    #     if data is None:
    #         return
    #     self.datas.append(data)

    def sqlite_open(self, dbpath=None):
        conn_sqlite = sqlite3.connect(dbpath)
        db1 = conn_sqlite.cursor()
        return db1

    def output_sqlite(self, dbpath=None):
        conn_sqlite = sqlite3.connect(dbpath)
        db1 = conn_sqlite.cursor()
        db1.execute()

    def sqlite_close(self, db1):
        db1.close()
        return None