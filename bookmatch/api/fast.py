import pandas as pd
from fastapi import FastAPI
from bookmatch.logic import *
from bookmatch.interface import *
from bookmatch.interface.main_local import postprocessing
import requests
from bookmatch.params import *

app = FastAPI()

# app.state.model = load_model()

# http://127.0.0.1:8000/predict?pickup_datetime=2012-10-06 12:10:20&pickup_longitude=40.7614327&pickup_latitude=-73.9798156&dropoff_longitude=40.6513111&dropoff_latitude=-73.8803331&passenger_count=2

@app.get("/predict")
def predict(movie_list):
    # model = load_model()
    # assert model is not None
    # book_list = app.state.model.predict(movie_list)
    # print(movie_list)
    csvname_cluster=f"X_bert_cluster_{str(N_CLUSTER)}.csv"

    # on retravaille movie list pour quil soit accepte par postprocessing
    input_movie=movie_list.split("$$$$$")

    input_movie=[int(elem) for elem in input_movie]

    reco = postprocessing(csvcluster=csvname_cluster,user_movies=input_movie)

    dico={"movie_list": input_movie,"book_list": list(reco.tolist())}

    return dico

@app.get("/")
def root():
    return {'greeting': 'Hello this API is functional'}



# if __name__== "__main__":

#     url = 'http://localhost:8000/predict'

#     # pour le moment postprocessing prend des item_id_movie en entree
#     movie_list = ["1","2","3","4","5","6","7","8","9","10",
#                   "11","12","13","14","15","16","17","18","19","20"]
#     # movie_list = ["1"]

#     texte = "$$$$$".join(movie_list)
#     params = {"movie_list":texte}

#     #test pour debug
#     # predict(movie_list=params)

#     # partie avec api
#     response = requests.get(url, params=params)
#     print(response.json())
