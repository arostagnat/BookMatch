import streamlit as st
import pandas as pd
import requests
import os
from pathlib import Path
import openai

local_raw_data_path = Path(__file__).parents[2].joinpath("data/raw_data")
file_path = Path(local_raw_data_path).joinpath("raw_movies/metadata.json")
metadata_movies = pd.read_json(file_path,lines = True)

st.set_page_config(
            page_title="BookMatch", # => Quick reference - Streamlit
            page_icon="https://em-content.zobj.net/thumbs/120/apple/325/open-book_1f4d6.png",
            layout="centered", # wide
            initial_sidebar_state="auto") # collapsed

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

bookmatch_url = 'http://localhost:8000/predict'
response = requests.get(bookmatch_url, params={"movie_list":movie_ids})

prediction = response.json()

# pred = prediction['']

st.markdown(f'### Book recommendations {prediction}')
