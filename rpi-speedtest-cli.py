import os
import re
import subprocess
import time
from influxdb import InfluxDBClient

testinterval = 5 #
writeCSV = false
writeInfluxDB = false

print('start')
try:
    testinterval = os.environ['TEST_INTERVAL']
except:
    pass

try:
    writeCSV = os.environ['WRITE_CSV']
except:
    pass

try:
    writeInfluxDB = os.environ['WRITE_INFLUXDB']
except:
    pass

response = subprocess.Popen('speedtest-cli --simple', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')

ping = re.findall('Ping:\s(.*?)\s', response, re.MULTILINE)
download = re.findall('Download:\s(.*?)\s', response, re.MULTILINE)
upload = re.findall('Upload:\s(.*?)\s', response, re.MULTILINE)

ping = ping[0].replace(',', '.')
download = download[0].replace(',', '.')
upload = upload[0].replace(',', '.')

if writeCSV
    try:
        f = open('./speedtest.csv', 'a+')
        if os.stat('./speedtest.csv').st_size == 0:
                f.write('Date,Time,Ping (ms),Download (Mbit/s),Upload (Mbit/s)\r\n')
    except:
        pass

    f.write('{},{},{},{},{}\r\n'.format(time.strftime('%m/%d/%y'), time.strftime('%H:%M'), ping, download, upload))

if writeInfluxDB
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
    client = InfluxDBClient('localhost', 8086, 'speedmonitor', 'pimylifeup', 'internetspeed')
    client.write_points(speed_data)



print(time.strftime('%m/%d/%y') + ', ' + time.strftime('%H:%M') + ' Ping: ' + str(ping) + ' ms, Download: ' + str(download) + ' Mbit/s Upload: '+ str(upload) + ' Mbit/s')
print('Waiting for ' + str(testinterval) + ' seconds')
time.sleep(testinterval) 
print('end')
