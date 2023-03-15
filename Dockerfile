FROM python:3.10.6-buster
#FROM tensorflow/tensorflow:2.10.0

COPY requirements_prod.txt /requirements.txt
COPY bookmatch /bookmatch
COPY data/clef_api_google_console.json /data/clef_api_google_console.json
COPY data/bert_data/X_bert_cluster_3000.csv /data/bert_data/X_bert_cluster_3000.csv
COPY data/raw_data/raw_movies/metadata.json /data/raw_data/raw_movies/metadata.json
COPY data/raw_data/raw_book/metadata.json /data/raw_data/raw_book/metadata.json

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD uvicorn bookmatch.api.fast:app --host 0.0.0.0 --port $PORT
