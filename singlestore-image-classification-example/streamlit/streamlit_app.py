# streamlit_app.py

import streamlit as st
import array
import binascii
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import pandas as pd
import pymysql

# Initialize connection.

def init_connection():
    return pymysql.connect(**st.secrets["singlestore"])

conn = init_connection()

def hex_to_vector(vector):
    vector_unhex = binascii.unhexlify(vector)
    vector_list = list(array.array("I", vector_unhex))
    return vector_list

img_idx = st.slider("Image Index", 0, 9999, 0)

img_df = pd.read_sql("""
SELECT img_vector
FROM tf_images
     INNER JOIN img_use ON use_id = img_use
WHERE use_name = 'Testing' AND img_idx = %s;
""", conn, params = ([str(img_idx)]))

vector_string = img_df["img_vector"][0]

img = np.array(hex_to_vector(vector_string)).reshape(28, 28)

fig = plt.figure(figsize = (1, 1))
plt.imshow(img, cmap = plt.cm.binary)
plt.axis("off")
st.pyplot(fig)

predictions_df = pd.read_sql("""
SELECT t_shirt_top, trouser, pullover, dress, coat, sandal, shirt, sneaker, bag, ankle_boot, class_name
FROM prediction_results
     INNER JOIN categories ON img_label = class_idx
WHERE img_idx = %s;
""", conn, params = ([str(img_idx)]))

classes = [
  "t_shirt_top",
  "trouser",
  "pullover",
  "dress",
  "coat",
  "sandal",
  "shirt",
  "sneaker",
  "bag",
  "ankle_boot"
]

num_classes = len(classes)

max_val = predictions_df[classes].max(axis = 1)[0]

predicted = (predictions_df[classes] == max_val).idxmax(axis = 1)[0]

actual = predictions_df["class_name"][0]

st.write("Predicted: ", predicted)
st.write("Actual: ", actual)

if (predicted == actual):
   st.write("Prediction Correct")
else:
   st.write("Prediction Incorrect")

probabilities = [predictions_df[class_name][0] for class_name in classes]

bar = px.bar(probabilities,
             x = classes,
             y = probabilities,
             color = probabilities,
             labels = dict(x = "Classes", y = "Probability"),
             title = "Prediction")

bar.update_xaxes(tickangle = 45)
bar.layout.coloraxis.colorbar.title = "Probability"

st.plotly_chart(bar)

st.table(predictions_df)
