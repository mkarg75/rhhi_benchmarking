#!/bin/python

# script to run the benchmarks against ds2 / ds3 stacks mostly automatically
# call logic:
# ./run_bench.py --stacks <number_of_stacks> --ds2 <number_of_ds2_containers> --ds3 <nr_of_ds3_containers> --threads <number_of_threads># -id <identifier>
# The containers will run with a consecutively increasing number which will be used to identify their specific DriverConfig.txt file
# container 0 will use  DriverConfig.txt.0 to map it into the container etc. 

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
import uuid

testdict = dict()

def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def ds2_subp(counter):
     typ = "ds2"
     cmd = 'docker run -t -v $(pwd)/DriverConfig.txt.' + str(counter) + ':/opt/app-root/app/driver_config.ini:Z dmesser/ds2mysqldriver:latest'
     proc = (subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE))
     testdict[proc] = typ

def ds3_supb(counter):
     typ = "ds3"
     cmd = 'docker run -t -v $(pwd)/DriverConfig.txt.' + str(counter) + ':/opt/app-root/app/driver_config.ini:Z dmesser/ds3mysqldriver:latest'
     proc = (subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE))
     testdic['proc'] = typ

def updatedb(result, typ, conn, stacks, threads, uid):
    #print "Running updatedb"
    for line in result.split("\n"):
       if "Final" in line:
           values = line.split()

    # Prepare the values so they fit into the db fields
    year = (values[1].split("/"))[2]
    day = (values[1].split("/"))[1]
    month = re.sub('[(]', '', (values[1].split("/"))[0])
    time = re.sub('[:)]', '', values[2])
    test_date = year + month + day + time
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
    rb_rate=values[21]
    rollback_rate = re.sub('[%]', '', rb_rate)
    #print "dstyp: ", typ
    #print "test_date: ", test_date
    #print "et: ", et
    #print "n_overall: ", n_overall
    #print "opm: ", opm
    #print "rt_tot_lastn_max: ", rt_tot_lastn_max
    #print "rt_tot_avg: ", rt_tot_avg
    #print "n_login_overall: ", n_login_overall
    #print "n_newcust_overall: ", n_newcust_overall
    #print "n_browse_overall: ", n_browse_overall
    #print "n_purchase_overall: ", n_purchase_overall
    #print "rt_login_avg_msec: ", rt_login_avg_msec
    #print "rt_newcust_avg_msec: ", rt_newcust_avg_msec
    #print "rt_browse_avg_msec: ", rt_browse_avg_msec
    #print "rt_purchase_avg_msec: ", rt_purchase_avg_msec
    #print "rt_tot_sampled: ", rt_tot_sampled
    #print "n_rollbacks_overall: ", n_rollbacks_overall
    #print "rollback_rate: ", rollback_rate

    # Insert the results into the DB
    x = conn.cursor()
    #print "Entering data into mysql"
    try:
        x.execute("""INSERT INTO results \
                 (idstring, uuid, test_date, threads, nr_stacks, et, n_overall, ds_typ, opm, rt_tot_lastn_max, rt_tot_avg, n_login_overall, n_newcust_overall, n_browse_overall, rt_login_avg_msec, rt_newcust_avg_msec, rt_browse_avg_msec, rt_purchase_avg_msec, n_purchase_overall,  rt_tot_sampled, n_rollbacks_overall, rollback_rate) VALUES \                 
                 (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", \
                 (idstring, uid, test_date, threads, stacks, et, n_overall, typ, opm, rt_tot_lastn_max, rt_tot_avg, n_login_overall, n_newcust_overall, n_browse_overall, rt_login_avg_msec, rt_newcust_avg_msec, rt_browse_avg_msec, rt_purchase_avg_msec, n_purchase_overall, rt_tot_sampled, n_rollbacks_overall, rollback_rate))                                 
        conn.commit()
        print "DB commit successful"
    except MySQLdb.Error as e:
        print "Error: ", e
        conn.rollback()

def main(argv):

    stacks = '0'
    ds2 = 0
    ds3 = 0
    threads = '0'
    idstring = ''

    try:
        opts, args = getopt.getopt(argv,"hs:d:e:t",["stacks=","ds2=","ds3=","threads="])
    except getopt.GetoptError:
        print 'run_bench.py -s <stacks> -d <ds2_instances> -e <ds3_instances> -t <threads>'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print 'run_bench.py -s <stacks> -d <ds2_instances> -e <ds3_instances> -t <threads>'
            sys.exit()
        elif opt in ("-s", "--stacks"):
            stacks = arg
            if stacks == 0:
                print "No stack number given, exiting."
                sys.exit(1)
        elif opt in ("-d", "--ds2"):
            ds2 = arg
        elif opt in ("-e", "--ds3"):
            ds3 = arg
        elif opt in ("-t", "--threads"):
            threads = arg
            if threads == 0:
                print "No thread number given, exiting."
                sys.exit(1)
        elif opt in ("-i" "--id"):
            idstring = arg
            if idstring == '':
                print "No identification string given, exiting"
                sys.exit(1)



    # Set up the DB connection
    try:
        conn = MySQLdb.connect(host= "192.168.104.18", user="root", db="benchmarking")
        print "Database connection succesfully established"
    except:
        print "No connection to the DB server"
        exit(0)

    # set the start date
    startdate = datetime.datetime.now()

    uid = str(uuid.uuid4())
    # run the docker instance(s) and collect the output 
    for i in range(0, ds2):
        print "Starting ds2 container number ", i
        ds2_subp(i)
    for j in range (0, ds3):
        print "Starting ds3 container number ", j
        ds3_subp(j)

    for key in testdict:
        #print key, testdict[key]
        key.wait()
        result = (key.communicate())[0]
        typ = (testdict[key])
        updatedb(result, typ, conn, stacks, threads, uid)

    print "All docker instances finished"

    # set the end date 
    enddate = datetime.datetime.now()

    # mark the area in grafana with start and end date from above
    #postdata = {"time": 'startdate', "isRegion": true, "timeEnd": enddate, "tags":["Start","End"],"text":"Benchmark Run"}
    #req = urllib2.Request('http://grafana.poc4.maxta.com/api/annotations')
    #req.add_header('Content-Type', 'application/json')

    #response = urllib.urlopen(req, json.dumps(postdata))
    # close the DB connection
    conn.close



if __name__ == "__main__":
   try:
      arg = sys.argv[1]
   except IndexError:
      print "Usage: run_bench.py -s <stacks> -d <ds2_instances> -e <ds3_instances> -t <threads> -i <id_string>"
      sys.exit()

   main(sys.argv[1:])

