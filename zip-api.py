import os
import requests
import zipfile
from flask import Flask, request, send_file, jsonify
from io import BytesIO

app = Flask(__name__)

# Function to download images and zip them
def download_and_zip_images(image_urls):
    folder_name = "downloaded_images"
    
    # Create folder to store images
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    # Download each image and save it in the folder
    for idx, url in enumerate(image_urls):
        try:
            image_data = requests.get(url).content
            image_path = os.path.join(folder_name, f'image_{idx + 1}.jpg')
            with open(image_path, 'wb') as f:
                f.write(image_data)
        except Exception as e:
            print(f"Failed to download image {url}: {e}")
            raise e

    # Create a zip file
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(folder_name):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, folder_name))

    # Clean up by removing the downloaded images after zipping
    for file in os.listdir(folder_name):
        os.remove(os.path.join(folder_name, file))
    os.rmdir(folder_name)

    # Move the zip buffer pointer to the start
    zip_buffer.seek(0)
    
    return zip_buffer

# Flask route to handle incoming POST requests with image URLs
@app.route('/upload', methods=['POST'])
def upload_and_zip_images():
    data = request.json
    image_urls = data.get('urls', [])

    if not image_urls:
        return jsonify({"error": "No image URLs provided."}), 400

    try:
        # Download images and create a zip file
        zipped_images = download_and_zip_images(image_urls)
        
        # Send the zip file as a response
        return send_file(zipped_images, mimetype='application/zip', as_attachment=True, attachment_filename='images.zip')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Flask app on external IP and port 7007
    app.run(host='0.0.0.0', port=7007)
