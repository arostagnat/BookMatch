from google.cloud import bigquery
from google.oauth2 import service_account
# from bookmatch.params import *
import pandas as pd

# En attente du .env
GCP_PROJECT="bookmatch-380010"
BQ_REGION="europe-west9"
BQ_DATASET="reviews"
KEY_PATH="/Users/rogze_lewagon/Documents/GCloud/bookmatch-380010-adeab148b29b.json"
GCP_REGION="europe-west9"
BUCKET_NAME="bookmatch"

def load_client():
    # Sort le client pour travailler sur Big Query
    credentials = service_account.Credentials.from_service_account_file(
    KEY_PATH, scopes=["https://www.googleapis.com/auth/cloud-platform"])

    return bigquery.Client(credentials=credentials, project=credentials.project_id)


def upload_data_reviews(data, table):
    # table = books ou reviews
    # Uniquement pour les reviews
    # Upload un dataframe sur Big Query

    full_table_name = f"{GCP_PROJECT}.{BQ_DATASET}.{table}"
    write_mode = "WRITE_APPEND"

    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)
    client = load_client()

    job = client.load_table_from_dataframe(data, full_table_name, job_config=job_config)
    _ = job.result()  # wait for the job to complete


def upload_all_reviews(path_reviews_processed, path_reviews_raw):
    print("Start save processed reviews ...\n")
    chunks = pd.read_csv(path_reviews_processed,
                       chunksize=1_000)
    table = "processed"
    count = 10
    for i, chunk in enumerate(chunks):
        chunk.replace("$$$", -1, inplace=True)
        if i == count:
            print(f"{i} chunks save")
            i += 10
        upload_data_reviews(chunk, table)

    print("Start save raw reviews ...\n")
    chunks = pd.read_csv(path_reviews_raw,
                       chunksize=1_000)
    table = "raw"
    count = 10
    for i, chunk in enumerate(chunks):
        chunk.replace("$$$", -1, inplace=True)
        if i == count:
            print(f"{i} chunks save")
            i += 10
        upload_data_reviews(chunk, table)

    print("\n\nEverithing is save ! ✅\n")



# Test only
if __name__ == "__main__":

    save = False

    if not save:
        print("""Pas de test disponible,\nsi vous voulez sauvegarder les données mettre save = True""")

    else:
        print("\nStart save 🏃\n\n")

        path_reviews_raw = "data/proc_data/X_raw_full_jsonlines.csv"
        path_reviews_processed = "data/proc_data/X_proc_full_jsonlines.csv"

        upload_all_reviews(path_reviews_processed, path_reviews_raw)
