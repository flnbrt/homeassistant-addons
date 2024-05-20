FROM python:3.12-slim

RUN pip install homeassistant
RUN mkdir /app
COPY run.sh /app/run.sh
COPY script.py /app/script.py
RUN chmod +x /app/run.sh

CMD [ "/app/run.sh" ]
