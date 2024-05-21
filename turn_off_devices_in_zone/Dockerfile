FROM python:3.12-slim

RUN pip install homeassistant-api
RUN mkdir /turn_off_devices_in_zone
COPY run.sh /turn_off_devices_in_zone/run.sh
COPY turn_off_devices_in_zone.py /turn_off_devices_in_zone/turn_off_devices_in_zone.py
RUN chmod +x /turn_off_devices_in_zone/run.sh

CMD [ "/turn_off_devices_in_zone/run.sh" ]
