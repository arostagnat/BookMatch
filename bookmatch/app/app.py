import streamlit as st
import pandas as pd
import datetime
import requests

URL = "/Users/egmac/code/arostagnat/BookMatch/data/raw_data/raw_movies/metadata.json"
metadata_movies = pd.read_json(URL,lines = True)

st.title("BookMatch")
st.markdown("""
You tell us your favorite films. We tell you the books to read.
""")

with st.form(key='params_for_api'):

    movie_titles = st.multiselect("What are some of your favorite movies?",
                                 metadata_movies["title"],max_selections=10)

    st.form_submit_button('Get my book reccs')

movie_ids = [metadata_movies[metadata_movies.title == title].item_id.values[0] for title in movie_titles]

# Add API url below

bookmatch_url = 'https://taxifare.lewagon.ai/predict'
response = requests.get(bookmatch_url, params=movie_ids)

prediction = response.json()

# pred = prediction['']

st.markdown(f'### Book recommendations')
