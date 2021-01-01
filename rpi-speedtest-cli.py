import os
import logging
import re
import subprocess
import time
import argparse
from influxdb import InfluxDBClient

def get_module_logger(mod_name):
    """
    To use this, do logger = get_module_logger(__name__)
    """
    logger = logging.getLogger(mod_name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    #return logger

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
__name__ = 'rpi-speedtest-cli'
    
# Initiate the parser
parser = argparse.ArgumentParser()

# Add long and short argument
parser.add_argument("--testinterval", "-t", help="set testinveral in s. [default = 300s (5 minutes)]", type=int)
parser.add_argument("--writeCSV", "-c", type=str2bool, nargs='?', const=True, default=writeCSV, help="set True/False to write CSV file. [default = True]")
parser.add_argument("--writeInfluxDB", "-i", type=str2bool, nargs='?', const=True, default=writeInfluxDB, help="set True/False to write into influxDB [default = True]")

# Read arguments from the command line
args = parser.parse_args()

# Check for --testinterval
if args.testinterval:
    testinterval=args.testinterval
    
# Check for --writeCSV
if args.writeCSV:
    writeCSV=args.writeCSV
    
# Check for --testinterval
if args.writeInfluxDB:
    writeInfluxDB=args.writeInfluxDB

get_module_logger(__name__).info("Set testinterval to %f seconds" % testinterval)
get_module_logger(__name__).info("Set writeCSV to %s" % writeCSV)
get_module_logger(__name__).info("Set writeInfluxDB to %s" % writeInfluxDB)

# conduct speedtest
get_module_logger(__name__).info("conduct speedtest")
response = subprocess.Popen('speedtest-cli --simple', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
ping = re.findall('Ping:\s(.*?)\s', response, re.MULTILINE)
download = re.findall('Download:\s(.*?)\s', response, re.MULTILINE)
upload = re.findall('Upload:\s(.*?)\s', response, re.MULTILINE)

ping = ping[0].replace(',', '.')
download = download[0].replace(',', '.')
upload = upload[0].replace(',', '.')

if writeCSV==True:
    get_module_logger(__name__).info('Write data to csv File')
    try:
        f = open('./speedtest.csv', 'a+')
        if os.stat('./speedtest.csv').st_size == 0:
                f.write('Date,Time,Ping (ms),Download (Mbit/s),Upload (Mbit/s)\r\n')
    except:
        pass

    f.write('{},{},{},{},{}\r\n'.format(time.strftime('%m/%d/%y'), time.strftime('%H:%M'), ping, download, upload))

if writeInfluxDB==True:
    get_module_logger(__name__).info('write data to influxDB')
    get_module_logger(__name__).info('create data for db')
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
    get_module_logger(__name__).info('connect to influxDB')
    client = InfluxDBClient(host='localhost', port=8086, database='speedtest', username='influxdb', password='spdtst')
    get_module_logger(__name__).info('write data to influxDB')
    client.write_points(speed_data)

get_module_logger(__name__).info(' Ping: ' + str(ping) + ' ms, Download: ' + str(download) + ' Mbit/s Upload: '+ str(upload) + ' Mbit/s')
get_module_logger(__name__).info('Waiting for ' + str(testinterval) + ' seconds')
time.sleep(testinterval)
