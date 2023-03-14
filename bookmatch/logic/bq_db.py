from google.cloud import bigquery
from google.oauth2 import service_account
from bookmatch.params import *
import pandas as pd
import os
import json


def load_client():
    # Sort le client pour travailler sur Big Query

    # Création de la clef API avec les informations dans le .env si elle n'existe pas
    if not os.path.isfile(KEY_PATH):
        key_dict = {"type": "service_account",
                    "project_id" : GCP_PROJECT,
                    "private_key_id" : PRIVATE_KEY_ID,
                    "private_key" : PRIVATE_KEY,
                    "client_email" : CLIENT_EMAIL,
                    "client_id" : CLIENT_ID,
                    "auth_uri" : AUTH_URI,
                    "token_uri" : TOKEN_URI,
                    "auth_provider_x509_cert_url" : AUTH_PROVIDER_X509_CERT_URL,
                    "client_x509_cert_url" : CLIENT_X509_CERT_URL}

        with open(KEY_PATH, "w") as file:
            json.dump(key_dict, file, indent=2)
        print("\n✅ Creation du fichier .json pour l'api de Google\nVisible dans le dossier data")

    # Connexion avec le projet sur Google Cloud (Big Query)
    credentials = service_account.Credentials.from_service_account_file(
    KEY_PATH, scopes=["https://www.googleapis.com/auth/cloud-platform"])

    return bigquery.Client(credentials=credentials, project=credentials.project_id)


def upload_data(data, bq_dataset, bq_table):
    """ Upload a DataFrame on BigQuery.
    If the DataFrame is big (>1000 lines), upload with chunks.

    Args:
        data (pd.DataFrame): The data for BigQuery
        bq_dataset (str): name of the dataset (folder)
        bq_table (str): explicit
    """

    print("\nRun upload_data 🏃\n")
    write_mode = "WRITE_TRUNCATE"
    full_table_name = f"{GCP_PROJECT}.{bq_dataset}.{bq_table}"

    if data.shape[0] <= 1000 :
        job_config = bigquery.LoadJobConfig(write_disposition=write_mode)
        client = load_client()

        job = client.load_table_from_dataframe(data, full_table_name, job_config=job_config)
        _ = job.result()

    # Split des gros DataFrame (+1000 lignes) pour ne pas faire planter big query
    else:
        # Création et ajout du premier chunk avec truncate
        start_split = 0
        end_split = 1000
        data_split = data.iloc[start_split : end_split]

        job_config = bigquery.LoadJobConfig(write_disposition=write_mode)
        client = load_client()

        job = client.load_table_from_dataframe(data_split, full_table_name, job_config=job_config)
        _ = job.result() # wait for the job to complete

        # Ajout des chunks restant avec append
        write_mode = "WRITE_APPEND"
        start_split = end_split
        end_split += 1000
        count = 0
        count_print = 10

        while end_split < data.shape[0]:
            data_split = None
            data_split = data.iloc[start_split : end_split]
            job_config = bigquery.LoadJobConfig(write_disposition=write_mode)
            client = load_client()
            job = client.load_table_from_dataframe(data_split, full_table_name, job_config=job_config)
            _ = job.result() # wait for the job to complete
            if count == count_print:
                print(f"{count} chunks done")
                count_print += 10
            start_split = end_split
            end_split += 1000

        # Ajout du dernier chunk si il existe
        if start_split <= data.shape[0]:
            data_split = None
            data_split = data.iloc[start_split:]
            job_config = bigquery.LoadJobConfig(write_disposition=write_mode)
            client = load_client()
            job = client.load_table_from_dataframe(data_split, full_table_name, job_config=job_config)
            _ = job.result() # wait for the job to complete

    print("\n✅ Upload finish !")
    return None


def download_data(bq_dataset, bq_table, data_size):
    print("\nRun download_data 🏃\n")

    if data_size != "full":
        query = f"""
        SELECT *
        FROM {GCP_PROJECT}.{bq_dataset}.{bq_table}
        LIMIT {data_size}
        """
    else:
        query = f"""
        SELECT *
        FROM {GCP_PROJECT}.{bq_dataset}.{bq_table}
        """

    client = load_client()
    query_job = client.query(query)
    result = query_job.result()
    print("\n✅ Download finish !")
    print("\nConverting query result into Dataframe")
    return result.to_dataframe()


# Test only
if __name__ == "__main__":

    # save = False

    # if not save:
    #     print("""Pas de test disponible,\nsi vous voulez sauvegarder les données mettre save = True""")

    # else:
    #     print("\nStart save 🏃\n\n")

    #     path_reviews_raw = "data/proc_data/X_raw_full_jsonlines.csv"
    #     path_reviews_processed = "data/proc_data/X_proc_full_jsonlines.csv"

    #     upload_all_reviews(path_reviews_processed, path_reviews_raw)
    # data = pd.DataFrame({"col1" : list(range(10_100)), "col2" : list(range(10_100))})
    # data = download_data(bq_dataset="reviews", bq_table="test2")
    # print(data.shape)
    # print(data.head())
    pass
