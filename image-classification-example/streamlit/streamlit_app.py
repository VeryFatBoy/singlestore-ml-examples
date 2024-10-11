# streamlit_app.py

import streamlit as st
import array
import binascii
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import sqlalchemy

# Initialise connection.
conn = st.connection("singlestore", type = "sql")

def hex_to_vector(vector):
    vector_unhex = binascii.unhexlify(vector)
    vector_list = list(array.array("I", vector_unhex))
    return vector_list

st.title("Image Classification Predictions")

# Image index slider
img_idx = st.slider("Image Index", 0, 9999, 0)

# Fetch image vector
stmt = f"""
    SELECT img_vector
    FROM tf_images
    INNER JOIN img_use ON use_id = img_use
    WHERE use_name = 'Testing' AND img_idx = {img_idx};
"""

img_df = conn.query(stmt)

# Check if image DataFrame is not empty
if not img_df.empty:
    vector_string = img_df["img_vector"][0]
    img = np.array(hex_to_vector(vector_string)).reshape(28, 28)

    # Display the image
    fig = plt.figure(figsize = (1, 1))
    plt.imshow(img, cmap=plt.cm.binary)
    plt.axis("off")
    st.pyplot(fig)
else:
    st.write("No image found for this index")

# Fetch predictions
stmt = f"""
    SELECT t_shirt_top, trouser, pullover, dress, coat, sandal, shirt, sneaker, bag, ankle_boot, class_name
    FROM prediction_results
    INNER JOIN categories ON img_label = class_idx
    WHERE img_idx = {img_idx};
"""

predictions_df = conn.query(stmt)

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

# Check if predictions DataFrame is not empty
if not predictions_df.empty:

    # Determine predicted class and actual class
    max_val = predictions_df[classes].max(axis = 1)[0]
    predicted = (predictions_df[classes] == max_val).idxmax(axis = 1)[0]
    actual = predictions_df["class_name"][0]

    st.write("Predicted: ", predicted)
    st.write("Actual: ", actual)

    if predicted == actual:
        st.write("Prediction Correct")
    else:
        st.write("Prediction Incorrect")

    probabilities = [predictions_df[class_name][0] for class_name in classes]

    # Create a bar chart for probabilities
    bar = px.bar(
        x = classes,
        y = probabilities,
        color = probabilities,
        color_continuous_scale = "inferno",
        labels = dict(x = "Classes", y = "Probability"),
        title = "Prediction"
    )

    bar.update_xaxes(tickangle = 45)
    bar.layout.coloraxis.colorbar.title = "Probability"

    st.plotly_chart(bar)

    # Display predictions DataFrame
    st.table(predictions_df)
else:
    st.write("No prediction results found for this image index")
