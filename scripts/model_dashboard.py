import streamlit as st
import requests

# Title of the app
st.title("Iris Flower Prediction")

# Input fields for the user to enter values
sepal_length = st.number_input("Sepal Length (cm)", min_value=0.0)
sepal_width = st.number_input("Sepal Width (cm)", min_value=0.0)
petal_length = st.number_input("Petal Length (cm)", min_value=0.0)
petal_width = st.number_input("Petal Width (cm)", min_value=0.0)

# Selectbox for choosing the model
model_name = st.selectbox("Select Model", ["predict_knn", "predict_logistic", "predict_random_forest", "predict_svm", "predict_decision_tree", "predict_naive_bayes", "predict_gradient_boosting", "predict_linear"])

# Button to make the prediction
if st.button("Predict"):
    # Prepare the data for the API request
    data = {
        "sepal_length": sepal_length,
        "sepal_width": sepal_width,
        "petal_length": petal_length,
        "petal_width": petal_width
    }
    
    # Call the API
    response = requests.post(f"http://127.0.0.1:8000/{model_name}", json=data)

    # Check if the request was successful
    if response.status_code == 200:
        prediction = response.json()
        st.success(f"Prediction: {prediction['prediction']}")
    else:
        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")