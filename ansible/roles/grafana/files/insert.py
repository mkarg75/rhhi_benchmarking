import MySQLdb
import time
import datetime

conn = MySQLdb.connect(host= "localhost",
        user="root",
        db="benchmarking")

x = conn.cursor()
ts = time.time()
st = datetime.dateime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
try:
    x.execute(""" INSERT INTO results VALUES (%s,%s) """, (123,345))
    conn.commit()
except:
    conn.rollback()

conn.close
