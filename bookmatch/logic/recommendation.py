import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from bookmatch.params import *
from pathlib import Path
import pickle

def get_data(csvcluster):
    #on va chercher le csv cluster
    # path_X_cluster=Path(LOCAL_CSV_BERT_PATH).joinpath("cluster_result")
    # filename_x_cluster=Path(path_X_cluster).joinpath(csvcluster)
    # X_cluster=pd.read_csv(filename_x_cluster)
    X_cluster=pd.read_csv(csvcluster)

    # on va chercher les meta mov
    # jsonmetamov="/Users/egmac/code/arostagnat/BookMatch/data/raw_data/raw_movies/metadata.json"
    jsonmetamov=Path(LOCAL_RAW_DATA_PATH).joinpath("raw_movies").joinpath("metadata.json")
    metadata_movies = pd.read_json(jsonmetamov, lines=True)

    # on va chercher les meta books
    # jsonmetabook="/Users/egmac/code/arostagnat/BookMatch/data/raw_data/raw_book/metadata.json"
    jsonmetabook=Path(LOCAL_RAW_DATA_PATH).joinpath("raw_book").joinpath("metadata.json")
    metadata_books = pd.read_json(jsonmetabook, lines=True)

    return X_cluster,metadata_movies,metadata_books

def post_processing(csvcluster):

    X_cluster,metadata_movies,metadata_books = get_data(csvcluster)

    X_cluster.item_id_movie = X_cluster.item_id_movie.astype(float)
    X_cluster.item_id_book = X_cluster.item_id_book.astype(float)

    # metadata_movies = # pd.read_json("/Users/egmac/code/arostagnat/BookMatch/data/raw_data/raw_movies/metadata.json", lines=True)
    # metadata_books = # pd.read_json("/Users/egmac/code/arostagnat/BookMatch/data/raw_data/raw_book/metadata.json", lines=True)
    metadata_movies.rename({"item_id":"item_id_movie", "title":"title_movie"}, axis='columns',inplace=True)
    # metadata_books.rename({"item_id":"item_id_book", "title":"title_book","img":"img_book","url":"url_book"}, axis='columns',inplace=True)
    metadata_books.rename({"item_id":"item_id_book", "title":"title_book"}, axis='columns',inplace=True)

    metadata_movies.item_id_movie = metadata_movies.item_id_movie.astype(float)
    metadata_books.item_id_book = metadata_books.item_id_book.astype(float)

    X_all = pd.merge(X_cluster, metadata_movies[["title_movie","item_id_movie"]], on="item_id_movie", how="left")
    # X_all = pd.merge(X_all, metadata_books[["title_book","item_id_book","url_book","img_book"]], on="item_id_book", how="left")
    X_all = pd.merge(X_all, metadata_books[["title_book","item_id_book"]], on="item_id_book", how="left")

    return X_all

def vector_processing(df_post_processing):

    X_all = df_post_processing
    vectors = X_all.vector.tolist()
    vectors_revised = []

    # In the current X_all, the vectors are inputted as lists, so they need to be converted

    for vector in vectors:
        result = vector.strip('[]').replace("\n","").replace("'","").replace(",","").split(' ')
        result = [float(i) for i in result if i!='']
        vectors_revised.append(result)




    X_vectors = pd.DataFrame(vectors_revised)

    # n = 250
    # X_vectors_revised = pd.DataFrame(X_vectors.iloc[:,0:n])


    X_vectors[["item_id_movie","item_id_book","is_movie"]] = X_all[["item_id_movie","item_id_book","is_movie"]]

    # return X_vectors_revised
    return X_vectors

def vector_movies_books(vector_revised):

    X_vectors_revised = vector_revised

    X_vectors_books = X_vectors_revised[X_vectors_revised.is_movie == 0].set_index("item_id_book",drop=True).drop(columns=["item_id_movie","is_movie"])

    X_vectors_movies = X_vectors_revised[X_vectors_revised.is_movie == 1].set_index("item_id_movie",drop=True).drop(columns=["item_id_book","is_movie"])

    return X_vectors_books,X_vectors_movies,

def before_recs(csvcluster):
    X_all = post_processing(csvcluster)

    X_vectors_revised = vector_processing(df_post_processing=X_all)

    X_vectors_books,X_vectors_movies =  vector_movies_books(vector_revised=X_vectors_revised)



    return X_all,X_vectors_books,X_vectors_movies


# def get_local_reccs(csvcluster,user_movies:list):
def get_local_reccs(user_movies:list):
    # X_all = post_processing(csvcluster)

    # X_vectors_revised = vector_processing(df_post_processing=X_all)

    # X_vectors_books,X_vectors_movies =  vector_movies_books(vector_revised=X_vectors_revised)

    # verified_movies = [movie_id for movie_id in user_movies if movie_id in X_all.item_id_movie.tolist()]

    verified_movies=user_movies

    filename1=Path(LOCAL_CSV_POSTPROCESS_PATH).joinpath("X_all.csv")
    filename2=Path(LOCAL_CSV_POSTPROCESS_PATH).joinpath("X_vect_b.csv")
    filename3=Path(LOCAL_CSV_POSTPROCESS_PATH).joinpath("X_vect_m.csv")

    X_all=pd.read_csv(filename1)

    X_vectors_movies=pd.read_csv(filename3)
    X_vectors_movies=X_vectors_movies.set_index("item_id_movie")

    X_vectors_books=pd.read_csv(filename2)
    X_vectors_books=X_vectors_books.set_index("item_id_book")

    # recommendations = pd.DataFrame(columns=["similarity","title_book","img_book","url_book"])
    recommendations = pd.DataFrame(columns=["similarity","title_book","img_book"])

    movies = pd.DataFrame(verified_movies,columns=["item_id_movie"])
    movies = pd.merge(movies,X_all[["title_movie","item_id_movie"]],on="item_id_movie",how="left")

    for movie_id in verified_movies:

        # Obtain vectors for user-inputted film and all books. Clusters are not used for time being
        movie_vector = X_vectors_movies[X_vectors_movies.index == movie_id]
        books_vectors = X_vectors_books

        # Calculate cosine similarity
        sim_books = cosine_similarity(books_vectors,movie_vector)

        # Create summary table of books with their similarity and relevant details
        sim_books_detail = pd.DataFrame(sim_books,index=books_vectors.index,columns=["similarity"])
        sim_books_detail = sim_books_detail.sort_values("similarity",ascending=False)
        # sim_books_detail = pd.merge(sim_books_detail,X_all[["title_book","img_book","url_book","item_id_book"]],
        #                             on="item_id_book",how="left")
        sim_books_detail = pd.merge(sim_books_detail,X_all[["title_book","item_id_book"]],
                                    on="item_id_book",how="left")

        # Add top book to recommendations dataframe
        top_book = pd.DataFrame([sim_books_detail.loc[0]])
        recommendations = pd.concat([recommendations,top_book],axis=0, ignore_index=True)

    print("Inputted films")
    print(movies)
    print(recommendations["title_book"])
    return recommendations["title_book"]

def get_global_reccs(user_movies:list):

    # X_all = post_processing(csvcluster)

    # X_vectors_revised = vector_processing(df_post_processing=X_all)

    # X_vectors_books,X_vectors_movies =  vector_movies_books(vector_revised=X_vectors_revised)

    # verified_movies = [movie_id for movie_id in user_movies if movie_id in X_all.item_id_movie.tolist()]

    verified_movies=user_movies

    filename1=Path(LOCAL_CSV_POSTPROCESS_PATH).joinpath("X_all.pickle")
    filename2=Path(LOCAL_CSV_POSTPROCESS_PATH).joinpath("X_vect_b.pickle")
    filename3=Path(LOCAL_CSV_POSTPROCESS_PATH).joinpath("X_vect_m.pickle")

    # Load data (deserialize)
    with open(filename1, 'rb') as handle:
        X_all = pickle.load(handle)
    # X_all=pd.read_csv(filename1)

    # Load data (deserialize)
    with open(filename3, 'rb') as handle:
        X_vectors_movies = pickle.load(handle)
    # X_vectors_movies=pd.read_csv(filename3)

    X_vectors_movies=X_vectors_movies.set_index("item_id_movie")

        # Load data (deserialize)
    with open(filename2, 'rb') as handle:
        X_vectors_books = pickle.load(handle)
    # X_vectors_books=pd.read_csv(filename2)

    X_vectors_books=X_vectors_books.set_index("item_id_book")


    ## Collect vectors of all inputted films and calculate average vector
    movies_id = pd.DataFrame(verified_movies,columns=["item_id_movie"])
    movies_vectors = pd.merge(movies_id,
                              X_vectors_movies,
                              how="left",
                              on="item_id_movie").set_index("item_id_movie")
    avg_movie_vector = pd.DataFrame([movies_vectors.mean(numeric_only=True)])
    books_vectors = X_vectors_books

    ## Calculate cosine similarity
    sim_books = cosine_similarity(books_vectors,avg_movie_vector)

    ## Create summary table of books with their similarity and relevant details
    sim_books_detail = pd.DataFrame(sim_books,index=books_vectors.index,columns=["similarity"])
    sim_books_detail = sim_books_detail.sort_values("similarity",ascending=False)
    # sim_books_detail = pd.merge(sim_books_detail,X_all[["title_book","img_book","url_book","item_id_book"]],on="item_id_book",how="left")
    sim_books_detail = pd.merge(sim_books_detail,X_all[["title_book","item_id_book"]],on="item_id_book",how="left")

    ## Take top 5 books and show results
    recommendations = sim_books_detail.head(5)
    movie_titles = pd.merge(movies_id,X_all[["title_movie","item_id_movie"]],how="inner",on="item_id_movie")
    print("Inputted films")
    print(movie_titles.title_movie)
    print ("Top 5 book recommendations")
    print(recommendations["title_book"])

    return recommendations["title_book"]
