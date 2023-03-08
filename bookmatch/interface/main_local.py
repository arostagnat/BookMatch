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

    from bookmatch.logic.data_v2 import Cleaner as clean


    chksize=2000#CHUNK_SIZE
    linesize=20000#DATA_SIZE

    movie_rev_raw_path = Path(LOCAL_RAW_DATA_PATH).joinpath("raw_movies", "reviews.json")
    book_rev_raw_path = Path(LOCAL_RAW_DATA_PATH).joinpath("raw_book", "reviews.json")

    mov_proc_path = Path(LOCAL_PROC_DATA_PATH).joinpath("proc_movies")
    book_proc_path = Path(LOCAL_PROC_DATA_PATH).joinpath("proc_book")
    # on cree les rep de preproc si pas deja fait
    for pth in [mov_proc_path, book_proc_path]:
        if not os.path.exists(pth):
            os.makedirs(pth)


    #on clean les rev de mov par chunk et on store 5 chunks par proc_test_i.csv
    readerm=pd.read_json(movie_rev_raw_path,
                    lines=True,chunksize=chksize,nrows=linesize,
                    encoding='utf-8', encoding_errors='replace')
    dftot,dftemp,dftot2=None,None,None
    i,p=1,0
    for chunk in readerm:
        dftemp=chunk.groupby("item_id", as_index=False).agg({"txt": " /// ".join})
        if dftot is None:
            dftot=dftemp
            dftot2=dftemp
        else:
            dftot=pd.concat([dftot,dftemp],ignore_index=True) #concat vertical
            dftot=dftot.groupby("item_id", as_index=False).agg({"txt": " /// ".join})

            dftot2=pd.concat([dftot2,dftemp],ignore_index=True) #concat vertical
            dftot2=dftot.groupby("item_id", as_index=False).agg({"txt": " /// ".join}) #concat txt par item_id
        p+=1
        ############## penser a coder clean par chunk et concat a la fin puis save
        if p==5:
            dftot=clean(dftot, return_tokenize=False)
            pathsavec=Path(mov_proc_path).joinpath(f"testm_chunk{i}.csv")
            dftot.to_csv(pathsavec,index=False,sep=",")

            pathsave=Path(mov_proc_path).joinpath(f"nc_testm_chunk{i}.csv")
            dftot2.to_csv(pathsave,index=False,sep=",")
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
        dftemp=chunk.groupby("item_id", as_index=False).agg({"txt": " /// ".join})
        if dftot is None:
            dftot=dftemp
        else:
            dftot=pd.concat([dftot,dftemp],ignore_index=True) #concat vertical
            dftot=dftot.groupby("item_id", as_index=False).agg({"txt": " /// ".join}) #concat txt par item_id
        p+=1
        if p==5:
            dftot=clean(dftot, return_tokenize=False)
            pathsave=Path(book_proc_path).joinpath(f"testb_chunk{i}.csv")
            dftot.to_csv(pathsave,index=False,sep=",")
            dftot=None
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
