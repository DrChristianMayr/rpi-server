import os
import sys
import re
import subprocess
import time
import argparse
from influxdb import InfluxDBClient

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
        

testinterval = 10 #
writeCSV = False
writeInfluxDB = False

# Initiate the parser
parser = argparse.ArgumentParser()
# Add long and short argument
parser.add_argument("--testinterval", "-t", help="set testinveral in s. [default = 300s (5 minutes)]", type=int)
parser.add_argument("--writeCSV", "-c", type=str2bool, nargs='?', const=True, default=writeCSV, help="set True/False to write CSV file. [default = True]")
parser.add_argument("--writeInfluxDB", "-i", type=str2bool, nargs='?', const=True, default=writeInfluxDB, help="set True/False to write into influxDB [default = True]")

# Read arguments from the command line
args = parser.parse_args()
print(args)

# Check for --testinterval
if args.testinterval:
    print("Set testinterval to %f seconds" % args.testinterval)
    testinterval=args.testinterval
    
# Check for --writeCSV
if args.writeCSV:
    print("Set writeCSV to %s" % args.writeCSV)
    writeCSV=args.writeCSV
    
# Check for --testinterval
if args.writeInfluxDB:
    print("Set writeInfluxDB to %s" % args.writeInfluxDB)
    writeInfluxDB=args.writeInfluxDB

# conduct speedtest
sys.stdout('conduct speedtest')
response = subprocess.Popen('speedtest-cli --simple', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
#response = subprocess.Popen('speedtest-cli', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
ping = re.findall('Ping:\s(.*?)\s', response, re.MULTILINE)
download = re.findall('Download:\s(.*?)\s', response, re.MULTILINE)
upload = re.findall('Upload:\s(.*?)\s', response, re.MULTILINE)

ping = ping[0].replace(',', '.')
download = download[0].replace(',', '.')
upload = upload[0].replace(',', '.')

if writeCSV==True:
    print('Write data to csv File')
    try:
        f = open('./speedtest.csv', 'a+')
        if os.stat('./speedtest.csv').st_size == 0:
                f.write('Date,Time,Ping (ms),Download (Mbit/s),Upload (Mbit/s)\r\n')
    except:
        pass

    f.write('{},{},{},{},{}\r\n'.format(time.strftime('%m/%d/%y'), time.strftime('%H:%M'), ping, download, upload))

if writeInfluxDB==True:
    print('write data to influxDB')
    print('create data for db')
    speed_data = [
        {
            "measurement" : "internet_speed",
            "tags" : {
                "host": "speedtest"
            },
            "fields" : {
                "download": float(download),
                "upload": float(upload),
                "ping": float(ping)
            }
        }
    ]
    print('connect to influxDB')
    client = InfluxDBClient(host='localhost', port=8086, database='speedtest', username='influxdb', password='spdtst')
    print('write data to influxDB')
    client.write_points(speed_data)

print(time.strftime('%m/%d/%y') + ', ' + time.strftime('%H:%M') + ' Ping: ' + str(ping) + ' ms, Download: ' + str(download) + ' Mbit/s Upload: '+ str(upload) + ' Mbit/s')
print('Waiting for ' + str(testinterval) + ' seconds')
time.sleep(testinterval)

print('end')
