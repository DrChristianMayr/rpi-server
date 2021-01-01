FROM python:3

# Add the python script
ADD rpi-speedtest-cli.py /

# Install required Python packages
RUN pip install speedtest-cli
RUN pip install influxdb

ARG tst_int=60
ARG wrt_csv=False
ARG wrt_iflxDB=True

ENV TEST_INTERVAL=$var_name
ENV WRITE_CSV=$wrt_csv
ENV WRITE_INFLUXDB=$wrt_iflxDB

# Set the working directory to /app
# in the container
#WORKDIR /app
CMD ["python", "./rpi-speedtest-cli.py"]
#CMD ["python", "-u", "./rpi-speedtest-cli.py", " -t $TEST_INTERVAL", " -c $WRITE_CSV", " -i $WRITE_INFLUXDB"]
