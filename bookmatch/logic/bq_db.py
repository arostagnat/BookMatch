from google.cloud import bigquery
from google.oauth2 import service_account
from bookmatch.params import *

# En attente du .env
GCP_PROJECT="bookmatch-380010"
BQ_REGION="europe-west9"
BQ_DATASET="bookmatch"
KEY_PATH="/Users/rogze_lewagon/Documents/GCloud/bookmatch-380010-adeab148b29b.json"
GCP_REGION="europe-west9"
BUCKET_NAME="bookmatch"

def load_client():
    # Sort le client pour travailler sur Big Query
    credentials = service_account.Credentials.from_service_account_file(
    KEY_PATH, scopes=["https://www.googleapis.com/auth/cloud-platform"])

    return bigquery.Client(credentials=credentials, project=credentials.project_id)


def upload_data_cleaned(data, table):
    # table = books ou reviews
    # Uniquement pour les reviews
    # Upload un dataframe sur Big Query

    # Parce que vous ne lisez pas
    try:
        assert table == "books" or table == "reviews"
    except:
        print("Erreur : demande à ton maître")
        return None

    full_table_name = f"{GCP_PROJECT}.{BQ_DATASET}.reviews_{table}_cleaned"
    write_mode = "WRITE_TRUNCATE"

    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)
    client = load_client()

    print("Run save ...")
    job = client.load_table_from_dataframe(data, full_table_name, job_config=job_config)
    _ = job.result()  # wait for the job to complete

    print("✅ Save to Big Query !!")


# Test only
if __name__ == "__main__":
    print("\nStart test 🏃\n\n")

    print("... pourquoi faire ?")
