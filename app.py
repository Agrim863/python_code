import streamlit as st
import pandas as pd
import requests

# Load ingredient data and normalize case
ingredient_data = pd.read_csv('Book1.csv')
ingredient_data['ingredient'] = ingredient_data['ingredient'].str.lower()

# Function to calculate health score
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

# Initialize session state
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
    st.session_state.barcode_data = None

# UI Components
if st.session_state.user_name is None:
    st.title("Health Scorer App")
    st.image('logo.png', width=300)  # Increased logo size
    st.markdown("<h1 style='text-align: center;'>Welcome to Health Scorer!</h1>", unsafe_allow_html=True)  # Centered title

    name = st.text_input("What's your Name?")
    if st.button("Start") and name:
        st.session_state.user_name = name
        st.experimental_rerun()  # Restart the app to show barcode scanner
else:
    st.markdown(f"<h1 style='text-align: center;'>Welcome, {st.session_state.user_name}!</h1>", unsafe_allow_html=True)
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
    barcode_data = st.text_input("Scanned barcode data:", value=st.session_state.barcode_data)

    if barcode_data:
        product_name, ingredients_text, image_url = get_product_details_by_barcode(barcode_data)
        
        if ingredients_text:
            st.image(image_url, width=200)  # Display product image
            st.write(f"Product Name: {product_name}")
            st.write(f"Ingredients: {ingredients_text}")
            ingredient_list = [ingredient.strip() for ingredient in ingredients_text.split(',')]
            health_score = calculate_health_score(ingredient_list, ingredient_data)

            # Determine category and set background color
            if health_score >= 71:
                category = "Healthy"
                color = "green"
            elif health_score >= 46:
                category = "Neutral"
                color = "yellow"
            elif health_score >= 21:
                category = "Unhealthy"
                color = "orange"
            else:
                category = "Slow Poison"
                color = "red"

            # Set the background color based on the category
            st.markdown(f"<div style='background-color: {color}; padding: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
            st.markdown(f"**Category: {category}**", unsafe_allow_html=True)
            st.write(f"Health Score: {health_score:.2f}")  # Show score with two decimal places
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("Ingredients not found.")

    # Store barcode data in session state
    if barcode_data:
        st.session_state.barcode_data = barcode_data
