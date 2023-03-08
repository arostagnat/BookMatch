import os
import numpy as np
import pandas as pd
# from google.cloud import bigquery
from pathlib import Path
# from colorama import Fore, Style
# from dateutil.parser import parse
from bookmatch.params import *

def preprocess(saveraw=0):
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
    linesize=100_000#DATA_SIZE

    ###  on fait deux readers pour movies et books

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
            ## on clean le chunk_flat
            chunk_flat_clean=clean(chunk_flat, return_tokenize=False,meth_clean_numb2=1)

            # on concat le chunk_flat_clean avec le precedent
            if dftot is None:
                dftot=chunk_flat_clean
            else:
                dftot=pd.concat([dftot,chunk_flat_clean],ignore_index=True) #concat vertical du tot avec le chunk clean
                dftot=flatten_txt(data=dftot,id="item_id",colname="txt") # on regroupe par item_id

            # rajout de concat des txt ra pour model bert de antoine
            if saveraw==1:
                if dftot_raw is None:
                    dftot_raw=chunk_flat_raw
                else:
                    dftot_raw=pd.concat([dftot_raw,chunk_flat_raw],ignore_index=True) #concat vertical du tot avec le chunk clean
                    dftot_raw=flatten_txt(data=dftot_raw,id="item_id",colname="txt")

        # en sortant de cette boucle on a dftot (et deftot_raw)


        #si c'est le premier passage on save les movies
        if readnum==1:
            path_csv_clean=Path(mov_proc_path).joinpath(f"mov_rev_clean_{str(linesize)}_linesize.csv")
            dftot.to_csv(path_csv_clean,index=False,sep=",")
            if saveraw==1:
                path_csv_raw=Path(mov_proc_path).joinpath(f"mov_rev_raw_{str(linesize)}_linesize.csv")
                dftot_raw.to_csv(path_csv_raw,index=False,sep=",")

        #si c'est le second passage on save les books
        elif readnum==2:
            path_csv_clean=Path(book_proc_path).joinpath(f"book_rev_clean_{str(linesize)}_linesize.csv")
            dftot.to_csv(path_csv_clean,index=False,sep=",")
            if saveraw==1:
                path_csv_raw=Path(book_proc_path).joinpath(f"book_rev_raw_{str(linesize)}_linesize.csv")
                dftot_raw.to_csv(path_csv_raw,index=False,sep=",")


        readnum+=1 #permet de passer au reader suivant quand on ecrit csv



if __name__ == '__main__':
    try:
        preprocess(saveraw=0)
        # train()
        # pred()
    except:
        import sys
        import traceback
        import ipdb
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        ipdb.post_mortem(tb)
