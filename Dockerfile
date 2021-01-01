FROM python:3

RUN pip install influxdb

WORKDIR ./docker
COPY . . 
CMD ["rpi-speedtest-cli.py"]
ENTRYPOINT ["python3"]
