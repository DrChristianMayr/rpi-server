import os
import logging
import re
import subprocess
import time
from influxdb import InfluxDBClient

def db_exists():
    '''returns True if the database exists'''
    dbs = client.get_list_database()
    for db in dbs:
        if db['name'] == dbname:
            return True
    return False

def wait_for_server(host, port, nretries=5):
    '''wait for the server to come online for waiting_time, nretries times.'''
    url = 'http://{}:{}'.format(host, port)
    waiting_time = 1
    for i in range(nretries):
        try:
            requests.get(url)
            return 
        except requests.exceptions.ConnectionError:
            print('waiting for', url)
            time.sleep(waiting_time)
            waiting_time *= 2
            pass
    print('cannot connect to', url)
    sys.exit(1)

def connect_db(host, port, reset):
    '''connect to the database, and create it if it does not exist'''
    global client
    print('connecting to database: {}:{}'.format(host,port))
    client = InfluxDBClient(host, port, retries=5, timeout=1)
    wait_for_server(host, port)
    create = False
    if not db_exists():
        create = True
        print('creating database...')
        client.create_database(dbname)
    else:
        print('database already exists')
    client.switch_database(dbname)
    if not create and reset:
        client.delete_series(measurement=measurement)
        
def measure(nmeas):
    '''insert dummy measurements to the db.
    nmeas = 0 means : insert measurements forever. 
    '''
    i = 0
    if nmeas==0:
        nmeas = sys.maxsize
    for i in range(nmeas):
        x = i/10.
        y = math.sin(x)
        data = [{
            'measurement':measurement,
            'time':datetime.datetime.now(),
            'tags': {
                'x' : x
                },
                'fields' : {
                    'y' : y
                    },
            }]
        client.write_points(data)
        pprint.pprint(data)
        time.sleep(1)
        
def get_module_logger(mod_name):
    """
    To use this, do logger = get_module_logger(__name__)
    """
    logger = logging.getLogger(mod_name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
        

__name__ = 'rpi-speedtest-cli'

# Fetch environmental variables
testinterval = int(os.environ.get('TEST_INTERVAL',60))
writeCSV = str2bool(os.environ.get('WRITE_CSV',False))
writeInfluxDB = str2bool(os.environ.get('WRITE_INFLUXDB',True))
influxDBhost = os.environ.get('WRITE_INFLUXDB','localhost')
influxDBport = int(os.environ.get('WRITE_INFLUXDB',8086))
influxDBdatabase = os.environ.get('INFLUXDB_DB','speedtest')
influxDBusername = os.environ.get('INFLUXDB_USER','influxdb')
influxDBpassword = os.environ.get('INFLUXDB_PASSWORD','spdtst')

get_module_logger(__name__).info("Set testinterval to %d seconds" % testinterval)
get_module_logger(__name__).info("Set writeCSV to %s" % writeCSV)
get_module_logger(__name__).info("Set writeInfluxDB to %s" % writeInfluxDB)
get_module_logger(__name__).info("Set influxDB host to %s" % influxDBhost)
get_module_logger(__name__).info("Set influxDB port to %d" % influxDBport)
get_module_logger(__name__).info("Set influxDB database to %s" % influxDBdatabase)
get_module_logger(__name__).info("Set influxDB username host to %s" % influxDBusername)
get_module_logger(__name__).info("Set influxDB password port to %s" % influxDBpassword)

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
    client = InfluxDBClient(host=influxDBhost, port=influxDBport, database=influxDBpassword, username=influxDBusername, password=influxDBpassword)
    get_module_logger(__name__).info('write data to influxDB')
    client.write_points(speed_data)

get_module_logger(__name__).info('Ping: ' + str(ping) + ' ms, Download: ' + str(download) + ' Mbit/s Upload: '+ str(upload) + ' Mbit/s')
get_module_logger(__name__).info('Waiting for ' + str(testinterval) + ' seconds')
time.sleep(testinterval)
