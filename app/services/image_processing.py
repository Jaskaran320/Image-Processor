from PIL import Image
import requests
from io import BytesIO
import os
import logging

PROCESSED_FOLDER = 'app/processed'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def compress_and_upload_image(image_url, product_name, image_index):
    try:
        response = requests.get(image_url, stream=True, timeout=10)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content))
        compressed_image = image.convert('RGB')
        output_buffer = BytesIO()
        compressed_image.save(output_buffer, format='JPEG', quality=50)
        output_buffer.seek(0)

        filename = f"{product_name.replace(' ', '_')}_image_{image_index}.jpg"
        filepath = os.path.join(PROCESSED_FOLDER, filename)
        os.makedirs(PROCESSED_FOLDER, exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(output_buffer.getvalue())
        output_url = f"http://localhost:8000/processed_images/{filename}"
        return output_url
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading image from {image_url}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error processing image from {image_url}: {e}")
        return None