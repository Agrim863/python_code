import streamlit as st
import pandas as pd

st.title("Health Scorer with Barcode Scanner")

# Load ingredient data
ingredient_data = pd.read_csv('Book1.csv')

def calculate_health_score(ingredient_list, data_frame):
    ingredient_scores = pd.Series(data_frame.score.values, index=data_frame.ingredient).to_dict()
    total_score = 0
    
    for ingredient in ingredient_list:
        score = ingredient_scores.get(ingredient, 1)  # Default to 1 if ingredient is not found
        total_score += score
    
    if len(ingredient_list) > 0:
        normalized_score = (total_score / (len(ingredient_list)*5)) # Adjusted for a 0-100 scale
    else:
        normalized_score = 0  # Base positive score if no ingredients are provided

    final_score = normalized_score + 0  # Add base value to ensure positive scores
    
    return max(0, min(100, final_score))  # Ensure score is within 0-100 range

# Embed the barcode scanner HTML with slower blue line animation
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
      animation: move 4s linear infinite; /* Increased duration to slow down the line */
      pointer-events: none; /* Make sure the line does not interfere with interactions */
    }
    @keyframes move {
      0% { transform: translateY(0); }
      50% { transform: translateY(100%); }
      100% { transform: translateY(0); }
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
      document.getElementById('result').innerText = `Barcode Data: ${barcode}`;
      window.parent.postMessage({ type: 'barcode-data', data: barcode }, '*');
    });

    window.addEventListener('message', function(event) {
      if (event.data.type === 'barcode-data') {
        document.getElementById('result').innerText = `Barcode Data: ${event.data.data}`;
        window.parent.postMessage({ type: 'barcode-data', data: event.data.data }, '*');
      }
    });
  </script>
</body>
</html>
'''

# Display the barcode scanner within the Streamlit app
st.components.v1.html(html_code, height=600, scrolling=True)

# Handle barcode data received from the scanner
def get_barcode_data():
    # The barcode data is expected to be sent from the HTML script via postMessage
    # This function would handle retrieving and processing that data
    # For simplicity, we're using a placeholder here
    return st.session_state.get('barcode_data', '')

# Manual input for barcode data as a backup
barcode_data = st.text_input("Enter barcode data (comma-separated ingredients):", value=get_barcode_data())

if barcode_data:
    ingredient_list = barcode_data.split(',')
    health_score = calculate_health_score(ingredient_list, ingredient_data)
    st.write(f"Health Score: {health_score}")

# Update session state with barcode data if available
if 'barcode_data' not in st.session_state:
    st.session_state['barcode_data'] = barcode_data
