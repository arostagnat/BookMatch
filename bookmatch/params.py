import os
import numpy as np

##################  VARIABLES  ##################
DATA_SIZE = 1_000 # prend les x premieres lignes du json; peut prendre "full" avec un string
CHUNK_SIZE = 100 # concat et clean chaque chunk de facon iterative

LOCAL_RAW_DATA_PATH =os.path.join(os.path.dirname(__file__),"..","data","raw_data")
LOCAL_PROC_DATA_PATH  =os.path.join(os.path.dirname(__file__),"..","data","proc_data")

N_CLUSTER = 69

STOPWORDS= ["film","movie","book"]

# GCP_PROJECT = "<your project id>" # TO COMPLETE
# GCP_PROJECT_WAGON = "wagon-public-datasets"
# BQ_DATASET = "taxifare"
# BQ_REGION = "EU"
# MODEL_TARGET = "local"
# ##################  CONSTANTS  #####################
# LOCAL_DATA_PATH = os.path.join(os.path.expanduser('~'), ".lewagon", "mlops", "data")
# LOCAL_REGISTRY_PATH =  os.path.join(os.path.expanduser('~'), ".lewagon", "mlops", "training_outputs")

# COLUMN_NAMES_RAW = ['fare_amount','pickup_datetime', 'pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude', 'passenger_count']

# DTYPES_RAW = {
#     "fare_amount": "float32",
#     "pickup_datetime": "datetime64[ns, UTC]",
#     "pickup_longitude": "float32",
#     "pickup_latitude": "float32",
#     "dropoff_longitude": "float32",
#     "dropoff_latitude": "float32",
#     "passenger_count": "int16"
# }

# DTYPES_PROCESSED = np.float32
