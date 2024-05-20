FROM python:3.12-slim

RUN pip install homeassistant-api
RUN mkdir /python_modules
COPY run.sh /python_modules/run.sh
COPY script.py /python_modules/turn_off_devices_in_zone.py
RUN chmod +x /python_modules/run.sh

CMD [ "/app/run.sh" ]
