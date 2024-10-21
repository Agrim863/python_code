import streamlit as st
import pandas as pd
import requests

# Load ingredient data and normalize case
ingredient_data = pd.read_csv('Book1.csv')
ingredient_data['ingredient'] = ingredient_data['ingredient'].str.lower()

# Define a function to calculate health score
def calculate_health_score(ingredient_list, data_frame):
    data_frame['ingredient'] = data_frame['ingredient'].str.lower()
    ingredient_scores = pd.Series(data_frame.score.values, index=data_frame.ingredient).to_dict()
    actual_score = sum(ingredient_scores.get(ingredient, 0) for ingredient in ingredient_list)
    max_possible_score = len(ingredient_list) * 5

    if max_possible_score > 0:
        health_score = (actual_score / max_possible_score) * 100
    else:
        health_score = 0

    return max(0, min(100, health_score))

# Function to get product details by barcode
def get_product_details_by_barcode(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        product_data = response.json()
        if product_data.get("status") == 1:
            product = product_data.get("product", {})
            name = product.get("product_name", "Product name not available")
            ingredients = product.get("ingredients_text", "Ingredients not available")
            image_url = product.get("image_url", "")
            return name, ingredients, image_url
        else:
            st.error("Product not found in the database.")
            return None, None, None
    else:
        st.error(f"Error: Unable to fetch data (Status code: {response.status_code})")
        return None, None, None

# UI Components
if 'user_name' not in st.session_state:
    st.title("Health Scorer App")
    st.image('assets/logo.png', width=200)  # Make sure the logo is in the assets folder
    if st.button("Start"):
        name = st.text_input("What's your Name?")
        if name:
            st.session_state.user_name = name
            st.experimental_rerun()  # Restart the app to show barcode scanner
else:
    st.title(f"Welcome, {st.session_state.user_name}!")
    st.subheader("Scan to see what you're actually eating!")
    
    # Barcode Scanner Code
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

        codeReader.listVideoInputDevices().then(videoInputDevices => {
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

        document.getElementById('restart-scanner').addEventListener('click', () => {
          codeReader.reset();
          startScanner();
        });
      </script>
    </body>
    </html>
    '''
    
    st.components.v1.html(html_code, height=600, scrolling=True)

    # Handle barcode data
    barcode_data = st.text_input("Scanned barcode data:")

    if barcode_data:
        product_name, ingredients_text, image_url = get_product_details_by_barcode(barcode_data)
        
        if ingredients_text:
            st.image(image_url, width=200)  # Display product image
            st.write(f"Product Name: {product_name}")
            st.write(f"Ingredients: {ingredients_text}")
            ingredient_list = [ingredient.strip() for ingredient in ingredients_text.split(',')]
            health_score = calculate_health_score(ingredient_list, ingredient_data)
            st.write(f"Health Score: {health_score}")
        else:
            st.error("Ingredients not found.")

    # Store barcode data in session state
    st.session_state['barcode_data'] = barcode_data
