# streamlit_app.py

import streamlit as st
import pandas as pd
import pymysql

# Initialize connection.

def init_connection():
    return pymysql.connect(**st.secrets["singlestore"])

conn = init_connection()

user_id = st.sidebar.number_input("Enter a User Id", min_value = 1, max_value = 6040)

# Perform query.

data = pd.read_sql("""
SELECT movies.title,
       movies.poster,
       DOT_PRODUCT(UNHEX(users.factors), UNHEX(movies.factors)) AS score
FROM users JOIN movies
WHERE users.id = %s
ORDER BY score DESC
LIMIT 10;
""", conn, params = ([str(user_id)]))

st.subheader("Movie Recommendations")

for i in range(10):
   cols = st.columns(1)
   cols[0].header(data["title"][i])
   cols[0].image(data["poster"][i], width = 200)
