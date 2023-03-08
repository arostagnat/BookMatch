import os
import numpy as np
import pandas as pd
# from google.cloud import bigquery
from pathlib import Path
# from colorama import Fore, Style
# from dateutil.parser import parse
from bookmatch.params import *

def preprocess():
    """
    Query and preprocess the raw dataset iteratively (by chunks).
    Then store the newly processed data on local hard-drive for later re-use.

    - If raw data already exists on local disk:
        - use `pd.read_csv(..., chunksize=CHUNK_SIZE)`

    a coder :
    - If raw data does not yet exists:
        - use `bigquery.Client().query().result().to_dataframe_iterable()`

    """

    from bookmatch.logic.data import Cleaner as clean

    # on definit les path locaux raw ou on va piocher les data.json
    movie_rev_raw_path = Path(LOCAL_RAW_DATA_PATH).joinpath("raw_movies", "reviews.json")
    book_rev_raw_path = Path(LOCAL_RAW_DATA_PATH).joinpath("raw_book", "reviews.json")

    # on definit les path locaux process pour stocker les proc_data.csv
    mov_proc_path = Path(LOCAL_PROC_DATA_PATH).joinpath("proc_movies")
    book_proc_path = Path(LOCAL_PROC_DATA_PATH).joinpath("proc_book")

    # on cree les rep de preproc en local si pas deja fait dans data/proc_data
    for pth in [mov_proc_path, book_proc_path]:
        if not os.path.exists(pth):
            os.makedirs(pth)

    ########################################################
    ########################################################

    # on va traiter les data par chunks
    chksize=10_000#CHUNK_SIZE
    linesize=500_000#DATA_SIZE

    readerm=pd.read_json(movie_rev_raw_path,
                    lines=True,chunksize=chksize,nrows=linesize,
                    encoding='utf-8', encoding_errors='replace')

    dftot,dftemp,dftot2=None,None,None

    # boucle for qui concat les txt de chaque chunk par item_id
    i,p=1,0
    dftot,dftemp=None,None
    for chunk in readerm:
        dftemp=chunk.groupby("item_id", as_index=False).agg({"txt": " ".join})
        if dftot is None:
            dftot=dftemp
        else:
            dftot=pd.concat([dftot,dftemp],ignore_index=True) #concat vertical
            dftot=dftot.groupby("item_id", as_index=False).agg({"txt": " ".join})
        p+=1
        ############## penser a coder clean par chunk et concat a la fin puis save
        if p==5:
            ## on clean un total de 5 chunks
            # dftot2=clean(dftot, return_tokenize=False)

            # #on save le csv clean
            # path_csv_clean=Path(mov_proc_path).joinpath(f"mov_chunk{i}_clean.csv")
            # dftot2.to_csv(path_csv_clean,index=False,sep=",")

            # on save le csv pas clean
            path_csv_raw=Path(mov_proc_path).joinpath(f"mov_chunk{i}_raw.csv")
            dftot.to_csv(path_csv_raw,index=False,sep=",")
            dftot,dftot2=None,None
            i+=1
            p=0



    #meme chose sur les livres
    readerb=pd.read_json(book_rev_raw_path,
                    lines=True,chunksize=chksize,nrows=linesize,
                    encoding='utf-8', encoding_errors='replace')
    dftot,dftemp=None,None
    i,p=1,0
    for chunk in readerb:
        dftemp=chunk.groupby("item_id", as_index=False).agg({"txt": " ".join})
        if dftot is None:
            dftot=dftemp
        else:
            dftot=pd.concat([dftot,dftemp],ignore_index=True) #concat vertical
            dftot=dftot.groupby("item_id", as_index=False).agg({"txt": " ".join})
        p+=1
        ############## penser a coder clean par chunk et concat a la fin puis save
        if p==5:
            ## on clean un total de 5 chunks
            # dftot2=clean(dftot, return_tokenize=False)

            # #on save le csv clean
            # path_csv_clean=Path(book_proc_path).joinpath(f"book_chunk{i}_clean.csv")
            # dftot2.to_csv(path_csv_clean,index=False,sep=",")

            # on save le csv pas clean
            path_csv_raw=Path(book_proc_path).joinpath(f"book_chunk{i}_raw.csv")
            dftot.to_csv(path_csv_raw,index=False,sep=",")
            dftot,dftot2=None,None
            i+=1
            p=0


if __name__ == '__main__':
    try:
        preprocess()
        # train()
        # pred()
    except:
        import sys
        import traceback
        import ipdb
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        ipdb.post_mortem(tb)
