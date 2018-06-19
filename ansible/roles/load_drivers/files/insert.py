import MySQLdb
import time
import datetime
import commands
import json
import urllib2

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

names = ['et', 'n_overall', 'opm', 'rt_tot_lastn_max', 'rt_tot_avg', 'n_login_overall', 'n_newcust_overall', 'n_browse_overall', 'n_purchase_overall', 'rt_login_avg_msec', 'rt_newcust_avg_msec', 'rt_browse_avg_msec', 'rt_purchase_avg_msec', 'rt_tot_sampled', 'n_rollbacks_overall', 'rollback_rate']

# todo: create the DriverConfig.txt file dynamically

ds_typ = "ds3"
threads = 60
nr_stacks = 24
et = 10
n_overall = 100
nr_open = 12
rt_tot_lastn_max = 321

# set the start date
startdate = datetime.datetime.now()

# run the docker instance and collect the output 
result = commands.getstatusoutput('docker run -it -v $(pwd)/DriverConfig.txt:/opt/app-root/app/driver_config.ini:Z dmesser/ds2mysqldriver:latest')
print result

# set the end date 
enddate = datetime.dateime.now()

# mark the area in grafana with start and end date from above
postdata = {"time": starttime, "isRegion": true, "timeEnd": enddate, "tags":["Start","End"],"text":"Benchmark Run"}
req = urllib2.Request('http://grafana.poc4.maxta.com/api/annotations')
req.add_header('Content-Type', 'application/json')

response = urllib.urlopen(req, json.dumps(postdata))

# parse the output 
for line in result.split("\n"):
    if "Final" in line:
        values = line.split()

# todo: fill the values from the output into the corresponding variables. 

try:
    conn = MySQLdb.connect(host= "localhost", user="root", db="benchmarking")
except:
    print "No connection to the DB server"
    exit(0)

x = conn.cursor()
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
try:
    x.execute(""" INSERT INTO results (test_date, ds_typ, threads, nr_stacks, et, n_overall, open, rt_tot_lastn_max, rt_tot_avg, n_login_overall, n_newcust_overall, n_browse_overall, n_purchase_overall, rt_login_avg_msec, rt_newcust_avg_msec, rt_browse_avg_msec, rt_purchase_avg_msec, rt_tot_sampled, n_rollbacks_overall, rollback_rate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                  (st, ds_typ, threads, nr_stacks, et, n_overall, nr_open, rt_tot_lastn_max, rt_tot_avg, n_login_overall, n_newcust_overall, n_browse_overall, n_purchase_overall, rt_login_avg_msec, rt_newcust_avg_msec, rt_browse_avg_msec, rt_purchase_avg_msec, rt_tot_sampled, n_rollbacks_overall, rollback_rate))
    conn.commit()
except:
    conn.rollback()

conn.close

