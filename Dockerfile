FROM python:3

RUN pip install influxdb

CMD ["rpi-speedtest-cli.py"]
ENTRYPOINT ["python3"]
