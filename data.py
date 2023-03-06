import pandas as pd
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
# Ne pas oublier de mettre dans le requirements.txt nltk

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


def Stripering(serie):
    # Fonction pour Cleaner, strip le texte en entrée
    # Ne mettre que la colonne
    return serie.apply(lambda x : x.strip())

def Tokenizer(serie):
    # Fonction utilisé par NLP_Clean, tokenise (split) le texte pour travailler dessus
    out = []
    for text in serie:
        out.append(word_tokenize(text))
    return pd.Series(out)

def Cleaner(data):
    print("Start Cleaner ...")

    # On strip
    print("Strip")
    data["txt"] = Stripering(data.txt)

    # On met en lower
    print("Lower")
    data["txt"] = data["txt"].apply(lambda x : x.lower())

    # On retire les nombres
    print("Remove numbers")
    temp = []
    for text in data.txt:
        temp.append("".join(word for word in text if not word.isdigit()))
    data["txt"] = temp

    # On retire la ponctuations
    print("Remove punctuations")
    temp = []
    for text in data.txt:
        for punctuation in string.punctuation:
            text = text.replace(punctuation, "")
        temp.append(text)
    data["txt"] = temp

    # On tokenise
    print("Run Tokeniser")
    data["txt"] = Tokenizer(data.txt)

    # Stopwords et lemmatizing
    print("Run Stopword and Lemmatizing")
    stopwords_list = set(stopwords.words("english"))
    temp_data = []
    count = 10000
    for i, text in enumerate(data.txt):

        if i == count:      # Compteur pour patienter
            print(f"{i} done ...")
            count += 10000

        temp_text = []
        for word in text:
            if not word in stopwords_list:
                word = WordNetLemmatizer().lemmatize(word, pos="v")
                word = WordNetLemmatizer().lemmatize(word, pos="n")
                temp_text.append(word)
        temp_data.append(temp_text)

    data["txt"] = temp_data

    print("Cleaner is finish !!")
    return data


# Test only
if __name__ == "__main__":
    # print("Start test")

    # Test de Sample_data
    # Sample_data()

    # Test de Cleaner
    # data = pd.DataFrame([[12,
    # "   Text for the test 72, with everithing ! "]], columns=["id_test", "txt"])
    # print(data.txt[0])
    # data = Cleaner(data)
    # print(data.txt[0])

    # Test perso Romain, clean le sample de reviews des films
    # data = pd.read_csv("raw_data/sample_movies_reviews.csv")
    # data = Cleaner(data)
    # data.to_csv("raw_data/sample_movies_reviews_clean.csv")
    # print("Data save")
    pass
