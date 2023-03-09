import pandas as pd
import numpy as np
import itertools
# import matplotlib.pyplot as plt
# %matplotlib inline
import pickle
import gensim.downloader as api

def get_data(meth=1):
    """ici on va coder les differents facon de choper le X_proc_raw
    1 - on le prend en local
    2 - on prend sur BQ
    3 - on prend dans ton fion
    """
    match meth:
        case 1:
            print("on prend la data en local")


        case 2:
            print("on prend la data sur bq")

        case 3:
            print("pas de fion detecte")

    pass

def cluster():
    get_data(meth=3)
