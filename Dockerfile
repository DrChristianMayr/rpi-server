FROM python:3

ADD rpi-speedtest-cli.py

RUN pip install influxdb

CMD [ "python", "./rpi-speedtest-cli.py" ]
