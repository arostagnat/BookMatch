import os
import numpy as np
import pandas as pd
# from google.cloud import bigquery
from pathlib import Path
# from colorama import Fore, Style
# from dateutil.parser import parse
from bookmatch.params import *

def preprocess(cleantype):
    """
    Query and preprocess the raw dataset iteratively (by chunks).
    Then store the newly processed data on local hard-drive for later re-use.
    """

    from bookmatch.logic.data import Cleaner as clean
    from bookmatch.utils import flatten_txt

    # on definit les path locaux raw ou on va piocher les data.json
    movie_rev_raw_path = Path(LOCAL_RAW_DATA_PATH).joinpath("raw_movies", "reviews.json")
    book_rev_raw_path = Path(LOCAL_RAW_DATA_PATH).joinpath("raw_book", "reviews.json")

    # on definit les path locaux process pour stocker les proc_data.csv
    # mov_proc_path = Path(LOCAL_PROC_DATA_PATH).joinpath("proc_movies")
    # book_proc_path = Path(LOCAL_PROC_DATA_PATH).joinpath("proc_book")

    # on cree les rep de preproc en local si pas deja fait dans data/proc_data
    # for pth in [mov_proc_path, book_proc_path]:
    #     if not os.path.exists(pth):
    #         os.makedirs(pth)

    ########################################################
    ########################################################

    # on va traiter les data par chunks
    chksize=CHUNK_SIZE # a tuner en fonction de la ram
    linesize=DATA_SIZE # sit tu veux tester sur les "linesize" premieres lignes du json
    # linesize="full"#DATA_SIZE   #si tu veux traiter le full json

    ###  on fait deux readers pour movies et books
    if linesize == "full":
        readerm=pd.read_json(movie_rev_raw_path,
                        lines=True,chunksize=chksize,
                        encoding='utf-8', encoding_errors='replace')

        readerb=pd.read_json(book_rev_raw_path,
                        lines=True,chunksize=chksize,
                        encoding='utf-8', encoding_errors='replace')

    else:
        readerm=pd.read_json(movie_rev_raw_path,
                        lines=True,chunksize=chksize,nrows=linesize,
                        encoding='utf-8', encoding_errors='replace')

        readerb=pd.read_json(book_rev_raw_path,
                        lines=True,chunksize=chksize,nrows=linesize,
                        encoding='utf-8', encoding_errors='replace')


    # on traite le premier reader puis le second
    readnum=1
    for reader in [readerm,readerb]:
        dftot=None
        dftot_raw=None
        for chunk in reader:
            chunk_flat=None
            #on concat les txt des item_id qui apparaissent dans plusieurs lignes
            chunk_flat=flatten_txt(data=chunk,id="item_id",colname="txt")
            chunk_flat_raw=chunk_flat.copy() #oblige de faire une copie du flatten_raw car le "clean" de romain ecrase la variable qu'on lui passe

            if cleantype==0:
                ## on clean le chunk_flat
                chunk_flat_clean=clean(chunk_flat, return_tokenize=False,jeff_method=1)

                # on concat le chunk_flat_clean avec le precedent
                if dftot is None:
                    dftot=chunk_flat_clean
                else:
                    dftot=pd.concat([dftot,chunk_flat_clean],ignore_index=True) #concat vertical du tot avec le chunk clean
                    dftot=flatten_txt(data=dftot,id="item_id",colname="txt") # on regroupe par item_id

                # rajout de concat des txt ra pour model bert de antoine
            elif cleantype==1:
                if dftot_raw is None:
                    dftot_raw=chunk_flat_raw
                else:
                    dftot_raw=pd.concat([dftot_raw,chunk_flat_raw],ignore_index=True) #concat vertical du tot avec le chunk clean
                    dftot_raw=flatten_txt(data=dftot_raw,id="item_id",colname="txt")

        # en sortant de cette boucle on a dftot (et deftot_raw)

        #si c'est le premier passage on save les movies
        if readnum==1:
            if cleantype==0:
                dftot_movies=dftot.copy()
                dftot_movies.rename(columns={"item_id":"item_id_movie"},inplace=True)
                dftot_movies['is_movie']=1

            elif cleantype==1:
                dftot_movies_raw=dftot_raw.copy()
                dftot_movies_raw.rename(columns={"item_id":"item_id_movie"},inplace=True)
                dftot_movies_raw['is_movie']=1


            #### code qui sauv en local dans un .csv
            # path_csv_clean=Path(mov_proc_path).joinpath(f"mov_rev_clean_{str(linesize)}_linesize.csv")
            # dftot.to_csv(path_csv_clean,index=False,sep=",")
            # if cleantype==1:
            #     path_csv_raw=Path(mov_proc_path).joinpath(f"mov_rev_raw_{str(linesize)}_linesize.csv")
            #     dftot_raw.to_csv(path_csv_raw,index=False,sep=",")

        #si c'est le second passage on save les books
        elif readnum==2:
            if cleantype==0:
                dftot_book=dftot.copy()
                dftot_book.rename(columns={"item_id":"item_id_book"},inplace=True)
                dftot_book['is_movie']=0

            elif cleantype==1:
                dftot_book_raw=dftot_raw.copy()
                dftot_book_raw.rename(columns={"item_id":"item_id_book"},inplace=True)
                dftot_book_raw['is_movie']=0

            # #### code qui sauv en local dans un .csv
            # path_csv_clean=Path(book_proc_path).joinpath(f"book_rev_clean_{str(linesize)}_linesize.csv")
            # dftot.to_csv(path_csv_clean,index=False,sep=",")
            # if cleantype==1:
            #     path_csv_raw=Path(book_proc_path).joinpath(f"book_rev_raw_{str(linesize)}_linesize.csv")
            #     dftot_raw.to_csv(path_csv_raw,index=False,sep=",")


        readnum+=1 #permet de passer au reader suivant quand on ecrit csv

    if cleantype==0:
        ### on concat mov et book
        X_prepro=pd.concat([dftot_movies,dftot_book],ignore_index=True).fillna(-1.).astype({'item_id_movie':'float64', 'txt':'str', 'is_movie':'float64', 'item_id_book':'float64'})

        ###on sauve cette df en local
        namecsv=f"X_proc_{str(linesize)}_jsonlines.csv"
        path_X_prepro=Path(LOCAL_PROC_DATA_PATH).joinpath(namecsv)
        X_prepro.to_csv(path_X_prepro,index=False,sep=",")
        X_out=X_prepro.copy()

    elif cleantype==1:
        X_raw=pd.concat([dftot_movies_raw,dftot_book_raw],ignore_index=True).fillna(-1.).astype({'item_id_movie':'float64', 'txt':'str', 'is_movie':'float64', 'item_id_book':'float64'})
        #on sauve cette df en local
        namecsv=f"X_raw_{str(linesize)}_jsonlines.csv"
        path_X_prepro=Path(LOCAL_PROC_DATA_PATH).joinpath(namecsv)
        X_raw.to_csv(path_X_prepro,index=False,sep=",")
        X_out=X_raw.copy()

    return namecsv#,X_out


def cluster_bro(csv):

    from bookmatch.logic.model_cluster import clusterbert

    X_cluster=clusterbert(csv)
    path_X_cluster=Path(LOCAL_PROC_DATA_PATH).joinpath("cluster_result")
    csvname_cluster=f"X_bert_cluster_{str(N_CLUSTER)}.csv"
    filename_x_cluster=Path(path_X_cluster).joinpath(csvname_cluster)
    if not path_X_cluster.exists():
        os.makedirs(path_X_cluster)
    X_cluster.to_csv(filename_x_cluster,index=False,sep=",")

    return csvname_cluster#,X_cluster

def postprocessing(csvcluster,user_movies):
    from bookmatch.logic.recommendation import get_global_reccs,get_local_reccs

    reco=get_local_reccs(csvcluster,user_movies)
    # reco2=get_global_reccs(csvcluster,user_movies)
    return reco

if __name__ == '__main__':


    #   il faudra coder une fonction qui choisit les item_id
    choice_movies=np.arange(20).tolist()

    csvprepro=f"X_raw_{str(DATA_SIZE)}_jsonlines.csv"
    csvname_cluster=f"X_bert_cluster_{str(N_CLUSTER)}.csv"

    #on cree le path proc s'il existe pas
    if not Path(LOCAL_PROC_DATA_PATH).exists():
        os.makedirs(LOCAL_PROC_DATA_PATH)
        csvprepro=preprocess(cleantype=CLEANTYPE)

    if not Path(LOCAL_PROC_DATA_PATH).joinpath("cluster_result").exists():
            csvname_cluster=cluster_bro(csv=csvprepro)

    postprocessing(csvcluster=csvname_cluster,user_movies=choice_movies)
