# streamlit_app.py

import streamlit as st
import pandas as pd
import sqlalchemy

# Initialise connection.
conn = st.connection("singlestore", type = "sql")

# Sidebar for user input
user_id = st.sidebar.number_input("Enter a User Id", min_value = 1, max_value = 6040)

# SQL statement to get movie recommendations
stmt = f"""
    SELECT movies.title, movies.poster,
        DOT_PRODUCT(UNHEX(users.factors), UNHEX(movies.factors)) AS score
    FROM users JOIN movies ON users.id = {user_id}
    ORDER BY score DESC
    LIMIT 10;
"""

# Execute the query and store results
data = conn.query(stmt)

# Check if any data returned and display recommendations
if not data.empty:
    st.subheader("Movie Recommendations")

    # Display recommended movies
    for i in range(len(data)):
        cols = st.columns(1)
        cols[0].header(data["title"][i])
        cols[0].image(data["poster"][i], width = 200)
else:
    st.write("No recommendations found.")
