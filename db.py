import sqlite3

class DB(object):
    def __init__(self, filename):
        self.conn = sqlite3.connect(filename, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def execute(self, *args):
        ret = self.cursor.execute(*args)
        self.conn.commit()
        return ret

    def __del__(self):
        self.conn.close()
