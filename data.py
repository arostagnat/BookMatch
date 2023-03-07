import pandas as pd
import numpy as np
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

def Sample_data():
    """Sample_data
    A partir du dossier raw_data, récupère une partie des reviexs pour les livres et les films.
    Attention, dans le dossier raw_data, avoir les dossiers raw_book et raw_movies
    """
    # On récupère toutes les données sous forme de chunk
    chunks_movies = pd.read_json("raw_data/raw_movies/reviews.json", lines=True,
                                 chunksize=100000,
                                 encoding='utf-8', encoding_errors='replace')
    chunks_book = pd.read_json("raw_data/raw_book/reviews.json", lines=True,
                               chunksize=100000,
                               encoding='utf-8', encoding_errors='replace')

    # Pour chaque chunk, on récupère un sample de 1000 lignes
    print("\nStart for movies\n")
    movies_sample = pd.DataFrame()
    for i, chunk in enumerate(chunks_movies):
        print(f"Start work chunk n° {i}")
        temp_sample = chunk.sample(n=2000, replace=False, random_state=1)
        movies_sample = pd.concat([movies_sample, temp_sample])

    print("\nStart for books\n")
    books_sample = pd.DataFrame()
    for i, chunk in enumerate(chunks_book):
        print(f"Start work chunk n° {i}")
        temp_sample = chunk.sample(n=2000, replace=False, random_state=1)
        books_sample = pd.concat([books_sample, temp_sample])

    # Remove all special characters
    print("\nRemove special characters ...\n")
    movies_sample.replace({r'[^\x00-\x7F]+':''}, regex=True, inplace=True)
    books_sample.replace({r'[^\x00-\x7F]+':''}, regex=True, inplace=True)

    # On sauvegarde dans des json
    movies_sample.to_json("raw_data/sample_movies_reviews.json")
    books_sample.to_json("raw_data/sample_books_reviews.json")
    print("\n✅ Data save !\n")

    return None


def Cleaner(data, return_tokenize=True):
    """Cleaner
    Clean the reviews :
    Strip, lower, punctuations, tokenise, remove stop word, lemmatizing.
    Args:
        data (pd.DataFrame): The all DataFrame of the reviews json,
                            or the reviews columns with the columns name "txt"
        return_tokenize (bool): Return the reviews tokenize (True), or a unique string.
                                Defaults to True.

    Returns:
        pd.DataFrame: the clean reviews
    """

    final_data = data.copy()

    print("\nStart Cleaner ...\n")
    # On strip
    print("Strip")
    data["txt"] = data["txt"].apply(lambda x : str(x).strip())

    # On met en lower
    print("Lower")
    data["txt"] = data["txt"].apply(lambda x : x.lower())

    # On retire les nombres
    print("Remove numbers")
    temp = []
    for text in data.txt:
        temp.append("".join(word for word in text if not word.isdigit()))
    data["txt"] = temp

    # On retire la ponctuations et caractères spéciaux (non-utf8)
    print("Remove punctuations")
    all_punctuation = string.punctuation + ""
    temp = []
    for text in data.txt:
        for punctuation in all_punctuation:
            text = text.replace(punctuation, "")
        temp.append(text)
    data["txt"] = temp

    # On tokenise
    print("Run Tokeniser")
    out = []
    for text in data.txt:
        out.append(word_tokenize(text))
    data["txt"] = out

    # Stopwords et lemmatizing
    print("Run Stopword and Lemmatizing")
    # Add word to be remove in the list bellow
    list_remove_word = [""]

    stopwords_list = stopwords.words("english") + list_remove_word
    temp_data = []
    count = 10_000
    for i, text in enumerate(data.txt):

        if i == count:      # Compteur pour patienter 🏃‍♀️
            print(f"{i} done ...")
            count += 10_000

        temp_text = []
        for word in text:
            if not word in stopwords_list:
                word = WordNetLemmatizer().lemmatize(word, pos="v")
                word = WordNetLemmatizer().lemmatize(word, pos="n")
                temp_text.append(word)

        if not temp_text:   # If the reviews haven't important word
            temp_text = np.nan

        temp_data.append(temp_text)

    # Prepare the data with the param return_tokenize
    if return_tokenize:
        data["txt"] = temp_data
    else:
        data["txt"] = [" ".join(review_list) for review_list in temp_data]

    # print(data.columns)
    final_data.drop("txt", axis=1, inplace=True)

    final_data = pd.concat([final_data, data.txt], axis=1)
    final_data.dropna(inplace=True)
    print("\n✅ Cleaner is finish !!\n")
    return final_data


# Test only
if __name__ == "__main__":
    print("\nStart test 🏃\n\n")

    # Test de Sample_data
    print("Start test Sample_data")
    Sample_data()

    # Test de Cleaner
    print("\nStart test Cleaner\n")
    data = pd.read_json("raw_data/sample_movies_reviews.json")
    data = Cleaner(data, return_tokenize=True)
    data.to_json("raw_data/sample_movies_reviews_clean.json")

    data2 = pd.read_json("raw_data/sample_books_reviews.json")
    data2 = Cleaner(data2, return_tokenize=True)
    data2.to_json("raw_data/sample_books_reviews_clean.json")

    print("✅ Data save\n")

    print("✅ End test ! 🙌\n")
