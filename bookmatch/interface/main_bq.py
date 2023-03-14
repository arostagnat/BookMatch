import os
import numpy as np
import pandas as pd
# from google.cloud import bigquery
from pathlib import Path
# from colorama import Fore, Style
# from dateutil.parser import parse
from bookmatch.logic.bq_db import upload_data, download_data
from bookmatch.params import *

def preprocess(cleantype):
    """
    Query and preprocess the raw dataset iteratively (by chunks).
    Then store the newly processed data on local hard-drive for later re-use.
    """

    from bookmatch.logic.data import Cleaner as clean
    from bookmatch.logic.data import Cleaner_light as clean_light
    from bookmatch.utils import flatten_txt

    # on va traiter les data par chunks
    chksize=CHUNK_SIZE # a tuner en fonction de la ram
    linesize=DATA_SIZE # sit tu veux tester sur les "linesize" premieres lignes du json

    # on definit les path locaux raw ou on va piocher les data.json
    movie_rev_raw_path = Path(LOCAL_RAW_DATA_PATH).joinpath("raw_movies", f"reviews_{DATA_SIZE}_lines.json")
    book_rev_raw_path = Path(LOCAL_RAW_DATA_PATH).joinpath("raw_book", f"reviews_{DATA_SIZE}_lines.json")

    if not (os.path.isfile(movie_rev_raw_path) and os.path.isfile(book_rev_raw_path)):
        print("on va dowloader from bq")
        df_raw_movies = download_data(bq_dataset="movies", bq_table="reviews",data_size=linesize)
        df_raw_books = download_data(bq_dataset="books", bq_table="reviews",data_size=linesize)

        dataraw_movies_path = Path(LOCAL_RAW_DATA_PATH).joinpath("raw_movies")
        if not dataraw_movies_path.exists():
            os.makedirs(dataraw_movies_path)

        dataraw_books_path = Path(LOCAL_RAW_DATA_PATH).joinpath("raw_book")
        if not dataraw_books_path.exists():
            os.makedirs(dataraw_books_path)

        df_raw_movies.to_json(movie_rev_raw_path,orient="records",lines=True)#, index=False, orient="table")
        df_raw_books.to_json(book_rev_raw_path,orient="records",lines=True)#, index=False, orient="table")


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

            if cleantype == (0 | 1):
                ## on clean le chunk_flat
                if cleantype == 0:
                    chunk_flat_clean=clean(chunk_flat, return_tokenize=False,jeff_method=1)
                elif cleantype == 1:
                    chunk_flat_clean=clean_light(chunk_flat,list_stop_words=STOPWORDS, see_evolution=True)


                # on concat le chunk_flat_clean avec le precedent
                if dftot is None:
                    dftot=chunk_flat_clean
                else:
                    dftot=pd.concat([dftot,chunk_flat_clean],ignore_index=True) #concat vertical du tot avec le chunk clean
                    dftot=flatten_txt(data=dftot,id="item_id",colname="txt") # on regroupe par item_id

                # rajout de concat des txt ra pour model bert de antoine
            elif cleantype==2:
                if dftot_raw is None:
                    dftot_raw=chunk_flat_raw
                else:
                    dftot_raw=pd.concat([dftot_raw,chunk_flat_raw],ignore_index=True) #concat vertical du tot avec le chunk clean
                    dftot_raw=flatten_txt(data=dftot_raw,id="item_id",colname="txt")

        # en sortant de cette boucle on a dftot (et/ou dftot_raw)

        #si c'est le premier passage on save les movies
        if readnum==1:
            if cleantype==(0 | 1):
                dftot_movies=dftot.copy()
                dftot_movies.rename(columns={"item_id":"item_id_movie"},inplace=True)
                dftot_movies['is_movie']=1

            elif cleantype==2:
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
            if cleantype==(0 | 1):
                dftot_book=dftot.copy()
                dftot_book.rename(columns={"item_id":"item_id_book"},inplace=True)
                dftot_book['is_movie']=0

            elif cleantype==2:
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

    if cleantype==(0 | 1):
        ### on concat mov et book
        X_prepro=pd.concat([dftot_movies,dftot_book],ignore_index=True).fillna(-1.).astype({'item_id_movie':'float64', 'txt':'str', 'is_movie':'float64', 'item_id_book':'float64'})

        ###on sauve cette df en local
        namecsv=f"X_proc_{str(linesize)}_jsonlines.csv"
        # path_X_prepro=Path(LOCAL_PROC_DATA_PATH).joinpath(namecsv)
        # X_prepro.to_csv(path_X_prepro,index=False,sep=",")
        X_out=X_prepro.copy()

    elif cleantype==2:
        X_raw=pd.concat([dftot_movies_raw,dftot_book_raw],ignore_index=True).fillna(-1.).astype({'item_id_movie':'float64', 'txt':'str', 'is_movie':'float64', 'item_id_book':'float64'})
        #on sauve cette df en local
        namecsv=f"X_raw_{str(linesize)}_jsonlines.csv"
        # path_X_prepro=Path(LOCAL_PROC_DATA_PATH).joinpath(namecsv)
        # X_raw.to_csv(path_X_prepro,index=False,sep=",")
        X_out=X_raw.copy()

    #on peut uplpoader sur bq, on sait jamais
    upload_data(data=X_out, bq_dataset="reviews", bq_table=namecsv[:-4])

    # return namecsv#,X_out
    return X_out


def cluster_bro(csv_prepro,csv_bert):

    from bookmatch.logic.model_cluster import clusterbert

    #clustering
    X_cluster=clusterbert(csv_prepro)

    # on upload sur bq
    bq_table = os.path.split(csv_bert)[-1][:-4]
    upload_data(data=X_cluster, bq_dataset="bert", bq_table=bq_table)

    # return csvname_cluster#,X_cluster
    return X_cluster

def postprocessing(csvcluster,user_movies):
    from bookmatch.logic.recommendation import get_global_reccs,get_local_reccs

    reco=get_local_reccs(csvcluster,user_movies)
    # reco2=get_global_reccs(csvcluster,user_movies)
    return reco

if __name__ == '__main__':

    # creation rep data si existe pas (necessaire pour clef api json)
    if not Path(LOCAL_DATA_PATH).exists():
        os.makedirs(Path(LOCAL_DATA_PATH))

    #on regarde si les data processed existent deja en local
    # processed_data peut prendre deux noms selon le choix du cleaner
    if CLEANTYPE == (0|1):
        csvprepro_filepath=Path(LOCAL_PROC_DATA_PATH).joinpath(f"X_proc_{str(DATA_SIZE)}_jsonlines.csv")
    elif CLEANTYPE == 2:
        csvprepro_filepath=Path(LOCAL_PROC_DATA_PATH).joinpath(f"X_raw_{str(DATA_SIZE)}_jsonlines.csv")


    # preprocessing
    if not os.path.isfile(csvprepro_filepath):
        if not Path(LOCAL_PROC_DATA_PATH).exists():
            os.makedirs(LOCAL_PROC_DATA_PATH)
        try: # on essaye de downloader depuis bq en priorite
            bq_table = os.path.split(csvprepro_filepath)[-1][:-4]
            X_processed = download_data(bq_dataset="reviews", bq_table=bq_table, data_size=DATA_SIZE)
        except: # si on a une erreur on lance le preprocess
            X_processed = preprocess(cleantype=CLEANTYPE) #rajouter une fonction bq upload dans preprocess
        #on sauve le dataframe X_proc en local
        X_processed.to_csv(csvprepro_filepath,index=False,sep=",")

    # bert clustering
    csvbert_filepath=Path(LOCAL_CSV_BERT_PATH).joinpath(f"X_bert_cluster_{str(N_CLUSTER)}.csv")
    if not os.path.isfile(csvbert_filepath):
        if not Path(LOCAL_CSV_BERT_PATH).exists():
            os.makedirs(LOCAL_CSV_BERT_PATH)
        try:
            bq_table = os.path.split(csvbert_filepath)[-1][:-4]
            X_cluster = download_data(bq_dataset="bert", bq_table=bq_table, data_size=DATA_SIZE)
        except:
            X_cluster = cluster_bro(csv_prepro=csvprepro_filepath,csv_bert=csvbert_filepath)
        X_cluster.to_csv(csvbert_filepath,index=False,sep=",")

    #post_processing

    #on a besoin des json metadata
    mov_metadata_filepath = Path(LOCAL_RAW_DATA_PATH).joinpath("raw_movies", "metadata.json")
    book_metadata_filepath = Path(LOCAL_RAW_DATA_PATH).joinpath("raw_book", "metadata.json")
    if not (os.path.isfile(mov_metadata_filepath) and os.path.isfile(book_metadata_filepath)):
        print("on va dowloader les metadata books et movies from bq")
        df_raw_metadata_movies = download_data(bq_dataset="movies", bq_table="metadata",data_size="full")
        df_raw_metadata_movies.to_json(mov_metadata_filepath,orient="records",lines=True,date_format='iso')#, index=False, orient="table")

        df_raw_metadata_books = download_data(bq_dataset="books", bq_table="metadata",data_size="full")
        df_raw_metadata_books.to_json(book_metadata_filepath,orient="records",lines=True,date_format='iso')#, index=False, orient="table")

    #input_liste_de_film
    choice_movies=np.arange(20).tolist()

    #post process
    postprocessing(csvcluster=csvbert_filepath,user_movies=choice_movies)


    # #   il faudra coder une fonction qui choisit les item_id
    # choice_movies=np.arange(20).tolist()

    # csvprepro=f"X_proc_{str(DATA_SIZE)}_jsonlines.csv"
    # csvname_cluster=f"X_bert_cluster_{str(N_CLUSTER)}.csv"
    # # preprocess(cleantype=CLEANTYPE)
    # cluster_bro(csv=csvprepro)




    #on cree le path proc s'il existe pas
    # if not Path(LOCAL_PROC_DATA_PATH).exists():
    #     os.makedirs(LOCAL_PROC_DATA_PATH)
    #     csvprepro=preprocess(cleantype=CLEANTYPE)

    # if not Path(LOCAL_PROC_DATA_PATH).joinpath("cluster_result").exists():
    #         csvname_cluster=cluster_bro(csv=csvprepro)

    # postprocessing(csvcluster=csvname_cluster,user_movies=choice_movies)
