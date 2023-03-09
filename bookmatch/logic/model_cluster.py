from pathlib import Path
import pandas as pd
import numpy as np
import itertools
# import matplotlib.pyplot as plt
# %matplotlib inline
import pickle
import gensim.downloader as api
from bookmatch.params import *
from alive_progress import alive_bar


def get_data(csvname,meth=1):
    """_summary_

    Args:
        csvname (str, optional): csv filename with extension . Defaults to "X_proc".
        meth (int, optional): 1 : local, 2: bq, 3: bonus. Defaults to 1.

    Returns:
        _type_: _description_
    """
    match meth:
        case 1:
            print("loading data")
            filepath=Path(LOCAL_PROC_DATA_PATH).joinpath(csvname)
            df=pd.read_csv(filepath)
            print("done.")
            return df


        case 2:
            print("on prend la data sur bq")

        case 3:
            print("pas de fion detecte")



def clusterbert(csvname):

    from sklearn.cluster import KMeans, MiniBatchKMeans, AgglomerativeClustering, Birch, BisectingKMeans
    from sentence_transformers import SentenceTransformer

    # on charge le X_proc
    X_reviews= get_data(csvname,meth=1)

    # on charge le modele bert

    # pathbert=Path(LOCAL_PROC_DATA_PATH).joinpath("model").joinpath("bert").joinpath("bert_embeddings.pickle")


    # partie du code en attente si besoin de gerer le .picle du modele transformer

    # if pathbert.is_file(): #alors on va le chercher en local

    #     with open(pathbert,'rb') as handle:
    #         bert_embeddings = pickle.load(handle)

    # else: # on telecharge le model de 90mo

    #     bert = SentenceTransformer('all-MiniLM-L6-v2')

    #     with open(pathbert,'wb') as handle:
    #         pickle.dump(bert_embeddings, handle, protocol=pickle.HIGHEST_PROTOCOL)

    bert = SentenceTransformer('all-MiniLM-L6-v2')

    print("bert encoding...")
    bert_embeddings = bert.encode(X_reviews["txt"])
    print("done.")

    print("AgglomerativeClustering...")
    clustering_bert = AgglomerativeClustering(n_clusters=N_CLUSTER).fit(bert_embeddings)
    print("done.")

    X_reviews.drop(columns="txt",inplace=True)
    X_reviews["clustering_label_bert"] = clustering_bert.labels_
    X_reviews["vector"] = bert_embeddings.tolist()


    return X_reviews
