from flask import Flask, request, jsonify
import pandas as pd
from werkzeug.utils import url_quote
from flask_cors import CORS
import streamlit as st

st.title("Health Scorer")
st.write("Capstone project")
app = Flask(__name__)
CORS(app)  # Enable CORS

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

@app.route('/process_data', methods=['POST'])
def process_data():
    # Get the QR code data from the request
    qr_code_data = request.get_json()['data']

    # Extract the ingredient information from the QR code data
    ingredient_list = extract_ingredients_from_qr_code(qr_code_data)

    # Calculate the health score
    health_score = calculate_health_score(ingredient_list, ingredient_data)

    # Generate a response to the user
    response = {'health_score': health_score}
    return jsonify(response)

@app.route('/test', methods=['GET'])
def test():
    # Your code for testing goes here
    pass

@app.route('/', methods=['GET'])
def index():
    return "Welcome to my Replit app!"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
