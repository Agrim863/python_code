import streamlit as st
import pandas as pd

st.title("Health Scorer with Barcode Scanner")

# Load ingredient data
ingredient_data = pd.read_csv('Book1.csv')

def calculate_health_score(ingredient_list, data_frame):
    ingredient_scores = pd.Series(data_frame.score.values, index=data_frame.ingredient).to_dict()
    total_score = sum(ingredient_scores.get(ingredient, 1) for ingredient in ingredient_list)
    
    if ingredient_list:
        normalized_score = (total_score / (len(ingredient_list) * 5))  # Adjusted for a 0-100 scale
    else:
        normalized_score = 0  # Base positive score if no ingredients are provided

    return max(0, min(100, normalized_score))  # Ensure score is within 0-100 range

# Embed the barcode scanner HTML
html_code = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Barcode Scanner with QuaggaJS</title>
  <script src="https://unpkg.com/quagga/dist/quagga.min.js"></script>
  <style>
    #scanner-container {
      position: relative;
    }
    #scanner {
      width: 100%;
      height: 400px;
      border: 1px solid black;
    }
    .scanner-line {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 4px;
      background: rgba(0, 0, 255, 0.7);
      animation: move 4s linear infinite;
    }
    @keyframes move {
      0% { top: 0; }
      50% { top: 100%; }
      100% { top: 0; }
    }
  </style>
</head>
<body>
  <h1>Barcode Scanner with QuaggaJS</h1>
  <div id="scanner-container">
    <video id="scanner"></video>
    <div class="scanner-line"></div>
  </div>
  <div id="result">Scan a barcode to see the result here.</div>
  <script>
    Quagga.init({
      inputStream: {
        type: "LiveStream",
        target: document.querySelector('#scanner'),
        constraints: {
          facingMode: "environment",
          width: { ideal: 640 },
          height: { ideal: 480 }
        }
      },
      decoder: {
        readers: ["code_128_reader", "ean_reader", "ean_8_reader", "upc_reader", "upc_e_reader"]
      }
    }, function(err) {
      if (err) {
        console.error(err);
        return;
      }
      Quagga.start();
    });

    Quagga.onDetected(function(data) {
      const barcode = data.codeResult.code;
      window.parent.postMessage({ type: 'barcode-data', data: barcode }, '*');
    });
  </script>
</body>
</html>
'''

# Display the barcode scanner within the Streamlit app
st.components.v1.html(html_code, height=600, scrolling=True)

# Handle barcode data received from the scanner
barcode_data = st.text_input("Enter barcode data (comma-separated ingredients):")

if barcode_data:
    ingredient_list = barcode_data.split(',')
    health_score = calculate_health_score(ingredient_list, ingredient_data)
    st.write(f"Health Score: {health_score}")

# Store barcode data in session state
st.session_state['barcode_data'] = barcode_data
