import pandas as pd
from fastapi import FastAPI
from bookmatch.logic import *
from bookmatch.interface import *
import requests

app = FastAPI()

# app.state.model = load_model()

# http://127.0.0.1:8000/predict?pickup_datetime=2012-10-06 12:10:20&pickup_longitude=40.7614327&pickup_latitude=-73.9798156&dropoff_longitude=40.6513111&dropoff_latitude=-73.8803331&passenger_count=2

@app.get("/predict")
def predict(movie_list):

    # model = load_model()
    # assert model is not None
    # book_list = app.state.model.predict(movie_list)
    book_list = ["this is a book list"]
    liste_finale = movie_list.split("$$$$$")

    return {"movie_list": liste_finale,
            "book_list": book_list}

@app.get("/")
def root():
    return {'greeting': 'Hello this API is functional'}

if __name__== "__main__":

    url = 'http://localhost:8080/predict'
    movie_list = ["spiderman", "harry potter", "can I get some burgers ?"]
    texte = "$$$$$".join(movie_list)
    params = {"movie_list":texte}

    response = requests.get(url, params=params)
    print(response.json())
