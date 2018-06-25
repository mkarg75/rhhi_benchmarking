#!/bin/python

import sys
import MySQLdb
import time
import datetime
import commands
import json
import urllib2
import re
import getopt
import subprocess

processes = []
testdict = dict()

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def ds2_subp(counter):
     type: ds3
     cmd = 'docker run -t -v $(pwd)/DriverConfig.txt.' + str(counter) + ':/opt/app-root/app/driver_config.ini:Z dmesser/ds2mysqldriver:latest'
     proc = (subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE))
     testdic['proc'] = type
     processes.append(proc)

def ds3_supb(counter)
     type: ds3
     cmd = 'docker run -t -v $(pwd)/DriverConfig.txt.' + str(counter) + ':/opt/app-root/app/driver_config.ini:Z dmesser/ds3mysqldriver:latest'
     proc = (subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE))
     testdic['proc'] = type
     processes.append(proc)

def updatedb(result):
    print "Running updatedb"
    for line in result.split("\n"):
       if "Final" in line:
           print line
           values = line.split()

    test_date = re.sub('[()]]', '', (values[1] + " " + values[2]))
    et = values[4]
    n_overall = (values[5].split("="))[1]
    opm = (values[6].split("="))[1]
    rt_tot_lastn_max = (values[7].split("="))[1]
    rt_tot_avg = (values[8].split("="))[1]
    n_login_overall=(values[9].split("="))[1]
    n_newcust_overall=(values[10].split("="))[1]
    n_browse_overall=(values[11].split("="))[1]
    n_purchase_overall=(values[12].split("="))[1]
    rt_login_avg_msec=(values[13].split("="))[1]
    rt_newcust_avg_msec=(values[14].split("="))[1]
    rt_browse_avg_msec=(values[15].split("="))[1]
    rt_purchase_avg_msec=(values[16].split("="))[1]
    rt_tot_sampled=(values[17].split("="))[1]
    n_rollbacks_overall=(values[18].split("="))[1]
    rollback_rate=values[21]
#    ds_type=values[22]

    print "Testdate: ", test_date
    print "et: ", et
    print "n_overall: ", n_overall
    print "opm: ", opm
    print "rt_tot_lastn_max: ", rt_tot_lastn_max
    print "rt_tot_avg: ", rt_tot_avg
    print "n_login_overall: ", n_login_overall
    print "n_newcust_overall: ", n_newcust_overall
    print "n_browse_overall: ", n_browse_overall
    print "n_purchase_overall: ", n_purchase_overall
    print "rt_login_avg_msec: ", rt_login_avg_msec
    print "rt_newcust_avg_msec: ", rt_newcust_avg_msec
    print "rt_browse_avg_msec: ", rt_browse_avg_msec
    print "rt_purchase_avg_msec: ", rt_purchase_avg_msec
    print "rt_tot_sampled: ", rt_tot_sampled
    print "n_rollbacks_overall: ", n_rollbacks_overall
    print "rollback_rate: ", rollback_rate

    # Insert the results into the DB
    x = conn.cursor()
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    print "Entering data into mysql"
    try:
#        x.execute(""" INSERT INTO results (test_date, ds_typ, threads, nr_stacks, et, n_overall, open, rt_tot_lastn_max, rt_tot_avg, n_login_overall, n_newcust_overall, n_browse_overall, n_purchase_overall, rt_login_avg_msec, rt_newcust_avg_msec, rt_browse_avg_msec, rt_purchase_avg_msec, rt_tot_sampled, n_rollbacks_overall, rollback_rate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", (st, ds_typ, threads, nr_stacks, et, n_overall, nr_open, rt_tot_lastn_max, rt_tot_avg, n_login_overall, n_newcust_overall, n_browse_overall, n_purchase_overall, rt_login_avg_msec, rt_newcust_avg_msec, rt_browse_avg_msec, rt_purchase_avg_msec, rt_tot_sampled, n_rollbacks_overall, rollback_rate))
        x.execute("""INSERT INTO results (threads, nr_stacks, et, n_overall) VALUES (%s, %s, %s,%s)""",(1, 2, et, n_overall))
        conn.commit()
        print "DB commit successful"
    except:
        conn.rollback()

# Set up the DB connection
try:
    conn = MySQLdb.connect(host= "localhost", user="root", db="benchmarking")
    print "Database connection succesfully established"
except:
    print "No connection to the DB server"
    exit(0)

# set the start date
startdate = datetime.datetime.now()

# run the docker instance(s) and collect the output 
for i in range(1, 5):
    print "Starting docker number ", i
    ds2_subp(i)
for key in testdict:
    print key, val
    key.wait()
    resultt = (key.communicate())[0]
    resultt.append(val)
    print result
    updatedb(result)


print "All docker instances finished"

# set the end date 
enddate = datetime.datetime.now()
print "enddate: ", enddate

# mark the area in grafana with start and end date from above
#postdata = {"time": 'startdate', "isRegion": true, "timeEnd": enddate, "tags":["Start","End"],"text":"Benchmark Run"}
#req = urllib2.Request('http://grafana.poc4.maxta.com/api/annotations')
#req.add_header('Content-Type', 'application/json')
#response = urllib.urlopen(req, json.dumps(postdata))
# close the DB connection
conn.close


