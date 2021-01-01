FROM python:3

RUN pip install speedtest-cli

RUN pip install influxdb





ARG tst_int=60
ARG wrt_csv=False
ARG wrt_iflxDB=True
ENV TEST_INTERVAL=$var_name
ENV WRITE_CSV=$wrt_csv
ENV WRITE_INFLUXDB=$wrt_iflxDB

WORKDIR ./docker
COPY . . 
CMD ["rpi-speedtest-cli.py -t TEST_INTERVAL -c WRITE_CSV -i WRITE_INFLUXDB"]
ENTRYPOINT ["python3"]
