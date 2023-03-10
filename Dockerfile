#FROM python:3.10.6-buster
FROM tensorflow/tensorflow:2.10.0

COPY requirements.txt /requirements.txt
COPY bookmatch /bookmatch

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD uvicorn bookmatch.api.fast:app --host 0.0.0.0 --port $PORT
