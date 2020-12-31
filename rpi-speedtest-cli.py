import os
import re
import subprocess
import time

testinterval=5 #
print('start')
try:
    testinterval=os.environ['TEST_INTERVAL']
except:
    pass

response = subprocess.Popen('speedtest-cli --simple', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
print(response)
ping = re.findall('Ping:\s(.*?)\s', response, re.MULTILINE)
download = re.findall('Download:\s(.*?)\s', response, re.MULTILINE)
upload = re.findall('Upload:\s(.*?)\s', response, re.MULTILINE)

ping = ping[0].replace(',', '.')
download = download[0].replace(',', '.')
upload = upload[0].replace(',', '.')

try:
    f = open('./speedtest.csv', 'a+')
    if os.stat('./speedtest.csv').st_size == 0:
            f.write('Date,Time,Ping (ms),Download (Mbit/s),Upload (Mbit/s)\r\n')
except:
    pass

f.write('{},{},{},{},{}\r\n'.format(time.strftime('%m/%d/%y'), time.strftime('%H:%M'), ping, download, upload))
print('Ping: ' + str(ping) + ' ms, Download: ' + str(download) + ' Mbit/s Upload: '+ str(upload) + ' Mbit/s')
print('Waiting for ' + str(testinterval) + ' seconds')
time.sleep(testinterval) 
print('end')
