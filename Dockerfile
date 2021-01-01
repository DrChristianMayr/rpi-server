FROM python:3

ADD rpi-speedtest-cli.py

CMD [ "python", "./rpi-speedtest-cli.py" ]
