import streamlit as st
import pandas as pd
import requests

st.title("Health Scorer with Barcode Scanner")

# Load ingredient data
ingredient_data = pd.read_csv('Book1.csv')

def calculate_health_score(ingredient_list, data_frame):
    ingredient_scores = pd.Series(data_frame.score.values, index=data_frame.ingredient).to_dict()
    total_score = sum(ingredient_scores.get(ingredient.lower(), 1) for ingredient in ingredient_list)
    
    if ingredient_list:
        normalized_score = (total_score / (len(ingredient_list) * 5))  # Adjusted for a 0-100 scale
    else:
        normalized_score = 0  # Base positive score if no ingredients are provided

    return max(0, min(100, normalized_score))  # Ensure score is within 0-100 range

def fetch_ingredients_from_barcode(barcode):
    """Fetch ingredients from Open Food Facts API using barcode"""
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        product_data = response.json()
        if 'product' in product_data and 'ingredients_text' in product_data['product']:
            ingredients = product_data['product']['ingredients_text']
            return ingredients.split(', ')  # Return a list of ingredients
    return []

# Embed the barcode scanner HTML using ZXing-JS
html_code = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ZXing Barcode Scanner</title>
  <script src="https://unpkg.com/@zxing/library@latest"></script>
  <style>
    #scanner-container {
      position: relative;
      width: 100%;
      height: 400px;
      border: 1px solid black;
    }
    video {
      width: 100%;
      height: 100%;
    }
    #result {
      margin-top: 20px;
      font-size: 1.2em;
    }
  </style>
</head>
<body>
  <div id="scanner-container">
    <video id="video"></video>
  </div>
  <div id="result">Scan a barcode to see the result here.</div>

  <script>
    const codeReader = new ZXing.BrowserBarcodeReader();
    const videoElement = document.getElementById('video');
    const resultElement = document.getElementById('result');

    codeReader.decodeFromVideoDevice(null, videoElement, (result, err) => {
      if (result) {
        resultElement.textContent = `Barcode Data: ${result.text}`;
        window.parent.postMessage({ type: 'barcode-data', data: result.text }, '*');
      }
      if (err && !(err instanceof ZXing.NotFoundException)) {
        console.error(err);
      }
    });
  </script>
</body>
</html>
'''

# Display the barcode scanner within the Streamlit app
st.components.v1.html(html_code, height=300, scrolling=True)

# Handle barcode data received from the scanner or manually entered
barcode_data = st.text_input("Enter barcode data (or scan to auto-fill):")

if barcode_data:
    ingredients_list = fetch_ingredients_from_barcode(barcode_data)
    if ingredients_list:
        health_score = calculate_health_score(ingredients_list, ingredient_data)
        st.write(f"Health Score: {health_score}")
        st.write(f"Ingredients: {', '.join(ingredients_list)}")
    else:
        st.write("Unable to fetch ingredients for this barcode.")
