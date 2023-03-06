import pandas as pd

def Sample_data():
    """Sample_data
    A partir du dossier raw_data, récupère une partie des reviexs pour les livres et les films.
    Attention, dans le dossier raw_data, avoir les dossiers raw_book et raw_movies
    """
    # On récupère toutes les données sous forme de chunk
    chunks_movies = pd.read_json("raw_data/raw_movies/reviews.json", lines=True, chunksize=100000)
    chunks_book = pd.read_json("raw_data/raw_book/reviews.json", lines=True, chunksize=100000)

    # Pour chaque chunk, on récupère un sample de 1000 lignes
    print("Start for movies")
    movies_sample = pd.DataFrame()
    for i, chunk in enumerate(chunks_movies):
        print(f"Start work chunk n° {i}")
        temp_sample = chunk.sample(n=1000, replace=False, random_state=1)
        movies_sample = pd.concat([movies_sample, temp_sample])

    print("Start for books")
    books_sample = pd.DataFrame()
    for i, chunk in enumerate(chunks_book):
        print(f"Start work chunk n° {i}")
        temp_sample = chunk.sample(n=1000, replace=False, random_state=1)
        books_sample = pd.concat([books_sample, temp_sample])

    # On sauvegarde dans des csv
    movies_sample.to_csv("raw_data/sample_movies_reviews.csv")
    books_sample.to_csv("raw_data/sample_books_reviews.csv")
    print("Data save !")

    return None

# Test only
if __name__ == "__main__":
    print("Start test")
    Sample_data()
