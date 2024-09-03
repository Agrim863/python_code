import streamlit as st
import pandas as pd

st.title("Health Scorer with QR Code Scanner")

# Load ingredient data
ingredient_data = pd.read_csv('Book1.csv')

def calculate_health_score(ingredient_list, data_frame):
    ingredient_scores = pd.Series(data_frame.score.values, index=data_frame.ingredient).to_dict()
    total_score = 0
    
    for ingredient in ingredient_list:
        score = ingredient_scores.get(ingredient, 1)  # Default to 1 if ingredient is not found
        total_score += score
    
    if len(ingredient_list) > 0:
        normalized_score = (total_score / (len(ingredient_list)*5))*100 # Adjusted for a 0-100 scale
    else:
        normalized_score = 0  # Base positive score if no ingredients are provided

    final_score = normalized_score + 0  # Add base value to ensure positive scores
    
    return max(0, min(100, final_score))  # Ensure score is within 0-100 range

# Embed the QR code scanner HTML
html_code = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>QR Code Scanner with jsQR</title>
  <script src="https://unpkg.com/jsqr/dist/jsQR.min.js"></script>
</head>
<body>
  <h1>QR Code Scanner with jsQR</h1>
  <video id="camera" width="100%" height="400px" style="border: 1px solid black;"></video>
  <div id="result">Scan a QR code to see the result here.</div>
  <script>
    const video = document.getElementById('camera');
    const result = document.getElementById('result');

    // Access the camera
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
      .then(stream => {
        video.srcObject = stream;
        video.setAttribute("playsinline", true); // Required for iOS
        video.play();
        scanQRCode();
      })
      .catch(err => {
        console.error('Error accessing camera: ', err);
      });

    function scanQRCode() {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');

      function tick() {
        if (video.readyState === video.HAVE_ENOUGH_DATA) {
          canvas.height = video.videoHeight;
          canvas.width = video.videoWidth;
          context.drawImage(video, 0, 0, canvas.width, canvas.height);
          const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
          const code = jsQR(imageData.data, canvas.width, canvas.height, {
            inversionAttempts: "dontInvert",
          });
          if (code) {
            result.innerText = `QR Code Data: ${code.data}`;
            window.parent.postMessage({ type: 'qr-code-data', data: code.data }, '*');
          }
        }
        requestAnimationFrame(tick);
      }

      tick();
    }

    // Listen for messages from the parent window
    window.addEventListener('message', function(event) {
      if (event.data.type === 'qr-code-data') {
        result.innerText = `QR Code Data: ${event.data.data}`;
        window.parent.postMessage({ type: 'qr-code-data', data: event.data.data }, '*');
      }
    });
  </script>
</body>
</html>
'''

# Display the QR code scanner within the Streamlit app
st.components.v1.html(html_code, height=600, scrolling=True)

# Handle QR code data received from the scanner
def get_qr_code_data():
    # The QR code data is expected to be sent from the HTML script via postMessage
    # This function would handle retrieving and processing that data
    # For simplicity, we're using a placeholder here
    return st.session_state.get('qr_code_data', '')

# Manual input for QR code data as a backup
qr_code_data = st.text_input("Enter QR code data (comma-separated ingredients):", value=get_qr_code_data())

if qr_code_data:
    ingredient_list = qr_code_data.split(',')
    health_score = calculate_health_score(ingredient_list, ingredient_data)
    st.write(f"Health Score: {health_score}")

# Update session state with QR code data if available
if 'qr_code_data' not in st.session_state:
    st.session_state['qr_code_data'] = qr_code_data
