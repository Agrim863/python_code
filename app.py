import streamlit as st
import pandas as pd
import requests
import streamlit.components.v1 as components
import urllib.parse

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

# Embed the barcode scanner HTML using jsQR with improved user experience
html_code = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>jsQR Barcode Scanner</title>
  <script src="https://cdn.jsdelivr.net/npm/jsqr/dist/jsQR.js"></script>
  <style>
    body { font-family: Arial, sans-serif; }
    #video { width: 100%; height: 60vh; border: 1px solid black; }
    #canvas { display: none; }
    #instructions { margin: 10px 0; font-size: 16px; color: #333; }
    #result { margin-top: 10px; font-size: 18px; color: green; }
  </style>
</head>
<body>
  <div id="instructions">Point your camera at a barcode. Ensure it's well-lit and within the frame.</div>
  <video id="video" autoplay></video>
  <canvas id="canvas"></canvas>
  <div id="result">Waiting for barcode...</div>

  <script>
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const resultElement = document.getElementById('result');
    const ctx = canvas.getContext('2d');
    const scanningInterval = 100;  // Scan every 100ms

    navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } }).then(stream => {
      video.srcObject = stream;
      video.setAttribute("playsinline", true); // required to tell iOS safari we don't want fullscreen
      video.play();
      requestAnimationFrame(tick);
    }).catch(err => {
      resultElement.innerText = 'Error accessing camera: ' + err.message;
    });

    function tick() {
      if (video.readyState === video.HAVE_ENOUGH_DATA) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const code = jsQR(imageData.data, imageData.width, imageData.height, {
          inversionAttempts: "dontInvert",
        });
        if (code) {
          resultElement.innerText = `Barcode Data: ${code.data}`;
          window.parent.postMessage({ type: 'barcode-data', data: code.data }, '*');
          return;  // Stop scanning once barcode is detected
        }
      }
      setTimeout(() => requestAnimationFrame(tick), scanningInterval);
    }

    window.addEventListener('message', function(event) {
      if (event.data.type === 'barcode-data') {
        window.location.href = `?barcode_data=${event.data.data}`;
      }
    });
  </script>
</body>
</html>
'''

# Display the barcode scanner within the Streamlit app
components.html(html_code, height=500, scrolling=True)

# Retrieve barcode data from URL parameters
query_params = urllib.parse.parse_qs(urllib.parse.urlsplit(st.experimental_get_query_params().get('barcode_data', '')).query)
barcode_data = query_params.get('barcode_data', [''])[0]

if barcode_data:
    ingredients_list = fetch_ingredients_from_barcode(barcode_data)
    if ingredients_list:
        health_score = calculate_health_score(ingredients_list, ingredient_data)
        st.write(f"Health Score: {health_score}")
        st.write(f"Ingredients: {', '.join(ingredients_list)}")
    else:
        st.write("Unable to fetch ingredients for this barcode.")
