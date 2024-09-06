import streamlit as st
import pandas as pd
import requests

st.title("Enhanced Health Scorer with Barcode Scanner")

# Load ingredient data and normalize case
ingredient_data = pd.read_csv('Book1.csv')
ingredient_data['ingredient'] = ingredient_data['ingredient'].str.lower()

def calculate_health_score(ingredient_list, data_frame):
    # Normalize case for the data frame
    data_frame['ingredient'] = data_frame['ingredient'].str.lower()
    
    # Create a dictionary of ingredient scores from the data frame
    ingredient_scores = pd.Series(data_frame.score.values, index=data_frame.ingredient).to_dict()
    
    # Debugging: Show ingredient scores
    st.write(f"Ingredient Scores: {ingredient_scores}")

    # Convert all ingredients in the list to lowercase
    ingredient_list = [ingredient.lower() for ingredient in ingredient_list]

    # Calculate the actual sum of the scores for the ingredients in the list
    actual_score = sum(ingredient_scores.get(ingredient, 0) for ingredient in ingredient_list)
    
    # Debugging: Show actual score
    st.write(f"Actual Score: {actual_score}")

    # The maximum possible score is the number of ingredients * 5
    max_possible_score = len(ingredient_list) * 5
    
    # Debugging: Show max possible score
    st.write(f"Max Possible Score: {max_possible_score}")

    # Calculate the normalized health score on a 0-100 scale
    if max_possible_score > 0:
        health_score = (actual_score / max_possible_score) * 100
    else:
        health_score = 0  # Default to 0 if no ingredients are provided

    return max(0, min(100, health_score))  # Ensure the score is between 0 and 100

def get_ingredients_by_barcode(barcode):
    # Open Food Facts API URL
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    
    # Send a GET request to the API
    response = requests.get(url)
    
    # Check if the response is successful
    if response.status_code == 200:
        product_data = response.json()
        
        # Check if the product exists in the database
        if product_data.get("status") == 1:
            product = product_data.get("product", {})
            ingredients = product.get("ingredients_text", "Ingredients not available")
            return ingredients
        else:
            st.error("Product not found in the database.")
            return None
    else:
        st.error(f"Error: Unable to fetch data (Status code: {response.status_code})")
        return None

# Enhanced ZXing barcode scanner with auto-focus, torch, and optimized format
html_code = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Enhanced ZXing Barcode Scanner</title>
  <script src="https://unpkg.com/@zxing/library@latest"></script>
  <style>
    #video {
      width: 100%;
      height: 400px;
      border: 1px solid black;
    }
    .controls {
      display: flex;
      justify-content: space-between;
      margin-top: 10px;
    }
  </style>
</head>
<body>
  <h1>Barcode Scanner with ZXing</h1>
  <video id="video"></video>
  <div class="controls">
    <button id="torch-toggle">Toggle Torch</button>
    <button id="restart-scanner">Restart Scanner</button>
  </div>
  <div id="result">Scan a barcode to see the result here.</div>

  <script>
    let selectedDeviceId;
    const codeReader = new ZXing.BrowserMultiFormatReader();
    const videoElement = document.getElementById('video');
    let torchEnabled = false;

    // Get camera devices and start the scanner
    codeReader.listVideoInputDevices().then(videoInputDevices => {
      // Use the first camera available
      selectedDeviceId = videoInputDevices[0].deviceId;
      startScanner();
    }).catch(err => console.error(err));

    function startScanner() {
      codeReader.decodeFromVideoDevice(selectedDeviceId, 'video', (result, err) => {
        if (result) {
          console.log(result.text);
          window.parent.postMessage({ type: 'barcode-data', data: result.text }, '*');
          document.getElementById('result').textContent = `Scanned Barcode: ${result.text}`;
        }
        if (err && !(err instanceof ZXing.NotFoundException)) {
          console.error(err);
        }
      });
    }

    // Toggle torch (flashlight)
    document.getElementById('torch-toggle').addEventListener('click', () => {
      const track = videoElement.srcObject.getVideoTracks()[0];
      const capabilities = track.getCapabilities();

      if (capabilities.torch) {
        torchEnabled = !torchEnabled;
        track.applyConstraints({
          advanced: [{ torch: torchEnabled }]
        });
      } else {
        alert('Torch is not available on this device.');
      }
    });

    // Restart scanner button
    document.getElementById('restart-scanner').addEventListener('click', () => {
      codeReader.reset();
      startScanner();
    });
  </script>
</body>
</html>
'''

# Display the enhanced barcode scanner within the Streamlit app
st.components.v1.html(html_code, height=600, scrolling=True)

# Handle barcode data received from the scanner
barcode_data = st.text_input("Scanned barcode data:")

if barcode_data:
    # Fetch ingredients using the Open Food Facts API
    ingredients_text = get_ingredients_by_barcode(barcode_data)
    
    if ingredients_text:
        st.write(f"Ingredients from barcode: {ingredients_text}")
        ingredient_list = [ingredient.strip() for ingredient in ingredients_text.split(',')]
        health_score = calculate_health_score(ingredient_list, ingredient_data)
        st.write(f"Health Score: {health_score}")
    else:
        st.error("Ingredients not found, please enter them manually.")

# Allow manual ingredient input if the API fails to retrieve ingredients
manual_ingredients = st.text_area("Enter ingredients manually (comma-separated):")

if manual_ingredients:
    ingredient_list = [ingredient.strip() for ingredient in manual_ingredients.split(',')]
    health_score = calculate_health_score(ingredient_list, ingredient_data)
    st.write(f"Health Score: {health_score}")

# Store barcode data in session state
st.session_state['barcode_data'] = barcode_data
