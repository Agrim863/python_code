import pandas as pd
import streamlit as st

st.title("Health Scorer")
st.write("Capstone project")

# Load ingredient data
ingredient_data = pd.read_csv('Book1.csv')

def calculate_health_score(ingredient_list, data_frame):
    ingredient_scores = pd.Series(data_frame.score.values, index=data_frame.ingredient).to_dict()
    total_score = 0
    for ingredient in ingredient_list:
        score = ingredient_scores.get(ingredient, 0)
        total_score += score
    normalized_score = (total_score / len(ingredient_list)*5)*100
    return normalized_score

def extract_ingredients_from_qr_code(qr_code_data):
    ingredient_list = [ingredient.strip() for ingredient in qr_code_data.split(',')]
    return ingredient_list

# Streamlit input for QR code data
qr_code_data = st.text_input("Enter QR code data (comma-separated ingredients):")

if qr_code_data:
    # Extract the ingredient information from the QR code data
    ingredient_list = extract_ingredients_from_qr_code(qr_code_data)

    # Calculate the health score
    health_score = calculate_health_score(ingredient_list, ingredient_data)

    # Display the health score
    st.write(f"Health Score: {health_score}")
