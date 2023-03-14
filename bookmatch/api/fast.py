import pandas as pd
from fastapi import FastAPI
from bookmatch.logic import *
from bookmatch.interface import *
from bookmatch.interface.main_bq import postprocessing
import requests
from bookmatch.params import *
from pathlib import Path

app = FastAPI()

@app.get("/predict")
def predict(movie_list):

    # csvname_cluster=f"X_bert_cluster_{str(N_CLUSTER)}.csv"
    csvbert_filepath=Path(LOCAL_CSV_BERT_PATH).joinpath(f"X_bert_cluster_{str(N_CLUSTER)}.csv")

    # on retravaille movie list pour quil soit accepte par postprocessing
    input_movie=movie_list.split("$$$$$") # a garder pour mode offciel
    # input_movie=movie_list["movie_list"].split("$$$$$") # mode debug

    input_movie=[int(elem) for elem in input_movie]

    reco = postprocessing(csvcluster=csvbert_filepath,user_movies=input_movie)

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

#     # # partie avec api
#     response = requests.get(url, params=params)
#     print(response.json())
