import streamlit as st
import pandas as pd
from streamlit.components.v1 import html

# Load ingredient data
ingredient_data = pd.read_csv('Book1.csv')

def calculate_health_score(ingredient_list, data_frame):
    ingredient_scores = pd.Series(data_frame.score.values, index=data_frame.ingredient).to_dict()
    total_score = 0
    for ingredient in ingredient_list:
        score = ingredient_scores.get(ingredient, 1)
        total_score += score
    
    if len(ingredient_list) > 0:
        normalized_score = (total_score / len(ingredient_list)) * 20
    else:
        normalized_score = 0

    return max(0, min(100, normalized_score))

# HTML for QR code scanner
html_code = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>QR Code Scanner</title>
  <script src="https://unpkg.com/html5-qrcode/minified/html5-qrcode.min.js"></script>
</head>
<body>
  <h1>QR Code Scanner</h1>
  <div id="qr-reader" style="width: 100%; height: 400px;"></div>
  <div id="qr-reader-results">Scan a QR code to see the result here.</div>
  <script>
    function onScanSuccess(qrCodeMessage) {
      console.log(`QR Code Data: ${qrCodeMessage}`);
      document.getElementById('qr-reader-results').innerText = `QR Code Data: ${qrCodeMessage}`;

      // Send the QR code data back to Streamlit
      fetch('/process_data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: qrCodeMessage })
      })
      .then(response => response.json())
      .then(data => {
        document.getElementById('qr-reader-results').innerText += `\nHealth Score: ${data.health_score}`;
      })
      .catch(error => console.error('Error:', error));
    }

    function onScanError(errorMessage) {
      console.warn(`QR Code Scan Error: ${errorMessage}`);
    }

    const html5QrCode = new Html5Qrcode("qr-reader");

    html5QrCode.start(
      { facingMode: "environment" },
      { fps: 10, qrbox: 250 },
      onScanSuccess,
      onScanError
    ).catch(err => {
      console.error(`QR Code Scan Error: ${err}`);
    });
  </script>
</body>
</html>
'''

# Display the QR code scanner
html(html_code, height=600)

# Manual input for QR code data
qr_code_data = st.text_input("Enter QR code data (comma-separated ingredients):")

if qr_code_data:
    ingredient_list = qr_code_data.split(',')
    health_score = calculate_health_score(ingredient_list, ingredient_data)
    st.write(f"Health Score: {health_score}")
