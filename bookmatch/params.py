import os

##################  VARIABLES  ##################
DATA_SIZE = 500_000 # prend les x premieres lignes du json; peut prendre "full" avec un string
CHUNK_SIZE = 10_000 # concat et clean chaque chunk de facon iterative

CLEANTYPE=1 # 0: full clean ou 1:clean_light pour bert 2: raw_data group by item_id

LOCAL_DATA_PATH=os.path.join(os.path.dirname(__file__),"..","data")
LOCAL_RAW_DATA_PATH =os.path.join(os.path.dirname(__file__),"..","data","raw_data")
LOCAL_PROC_DATA_PATH  =os.path.join(os.path.dirname(__file__),"..","data","processed_data")
LOCAL_CSV_BERT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "bert_data")

N_CLUSTER = 150

STOPWORDS= ["film","movie","book"] # pas utilise encore

# Clef API pour google
KEY_PATH = os.path.normpath(os.getenv("KEY_PATH"))
GCP_PROJECT = os.getenv("GCP_PROJECT")
PRIVATE_KEY_ID = os.getenv("PRIVATE_KEY_ID")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CLIENT_EMAIL = os.getenv("CLIENT_EMAIL")
CLIENT_ID = os.getenv("CLIENT_ID")
AUTH_URI = os.getenv("AUTH_URI")
TOKEN_URI = os.getenv("TOKEN_URI")
AUTH_PROVIDER_X509_CERT_URL = os.getenv("AUTH_PROVIDER_X509_CERT_URL")
CLIENT_X509_CERT_URL = os.getenv("CLIENT_X509_CERT_URL")

GCP_REGION = os.getenv("GCP_REGION")

# Clef api openAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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
