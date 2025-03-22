
# Import necessary libraries.
import streamlit as st
import pandas as pd
import numpy as np
import openai
from openai.embeddings_utils import get_embedding, cosine_similarity

#  Create a text input box for the user to enter the search terms.
user_input = st.text_input("Please let me know what you are looking for: ")

# Set the number of cards per row.
N_cards_per_row = 3

# If the user has entered the search terms, then perform the semantic search.
if user_input:
    # Get the word embedding of the user input.
    search_terms_vector = get_embedding(user_input, engine=engine)
    # Calculate the cosine similarity between each item name and the user input.
    df["similarity"] = df['embedding'].apply(lambda x: cosine_similarity(x, search_terms_vector))
    # Display the top 6 semantic-related items by highest similarity.
    df_result = df.sort_values("similarity", ascending=False).head(6)
    for n_row, row in df_result.reset_index().iterrows():
        i = n_row%N_cards_per_row # type: ignore
        if i==0:
            st.write("---")
            cols = st.columns(N_cards_per_row, gap="large")
        # draw the card
        with cols[n_row%N_cards_per_row]: # type: ignore
            st.caption(f"**{row['Item'].strip()}**")
            st.markdown(f"*{row['similarity']}*")
            st.image(f"{row['image']}", width = 200)
            st.button("Add to cart", key=cols[n_row%N_cards_per_row]) # type: ignore