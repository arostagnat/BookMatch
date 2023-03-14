FROM python:3.10.6-buster
#FROM tensorflow/tensorflow:2.10.0

COPY requirements_prod.txt /requirements.txt
COPY bookmatch /bookmatch
COPY data/proc_data/cluster_result/X_bert_cluster_69.csv /data/proc_data/cluster_result/X_bert_cluster_69.csv
COPY data/raw_data/raw_movies/metadata.json /data/raw_data/raw_movies/metadata.json
COPY data/raw_data/raw_book/metadata.json /data/raw_data/raw_book/metadata.json

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD uvicorn bookmatch.api.fast:app --host 0.0.0.0 --port $PORT
