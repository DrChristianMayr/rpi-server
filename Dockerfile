FROM python:3

RUN pip install influxdb

CMD [ "python", " rpi-speedtest-cli.py" ]
