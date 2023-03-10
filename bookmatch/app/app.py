import streamlit as st
import pandas as pd
import datetime
import requests

st.title("BookMatch")
st.markdown("""
You tell us your favorite films. We tell you the books to read.
""")

URL = "/Users/egmac/code/arostagnat/BookMatch/data/raw_data/raw_movies/metadata.json"
metadata_movies = pd.read_csv(URL,lines = True)

with st.form(key='params_for_api'):

    movie_titles = st.multiselect("What are some of your favorite movies?",
                                 metadata_movies["title"],max_selections=10)

    st.form_submit_button('Make prediction')

movie_ids = [metadata_movies[metadata_movies.title == title].item_id.values[0] for title in movie_titles]

bookmatch_url = 'https://taxifare.lewagon.ai/predict'
response = requests.get(bookmatch_url, params=movie_ids)

prediction = response.json()

# pred = prediction['fare']

st.header(f'Book recommendations: {prediction}')
