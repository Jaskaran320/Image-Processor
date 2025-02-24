# Image Processor

The Image Processor is designed to efficiently process image data from CSV files. It accepts a CSV file containing product information and image URLs, asynchronously processes these images (compressing them), and stores the processed image URLs and status. The API provides endpoints to upload CSV files, check processing status, and retrieve processed images. Celery is used for asynchronous task management to ensure efficient background processing.

## Setup

1.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv .spyne
    source .spyne/bin/activate  # On Linux/macOS
    .spyne\Scripts\activate  # On Windows
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Run the application

```bash
python app/main.py
```

## API Endpoints

### Upload CSV
- **Endpoint:** `/upload`
- **Method:** `POST`
- **Description:** Upload a CSV file containing product information and image URLs.
- **Request Body:** Form-data with a file field named `file`.
- **Response:**
    - `202 OK`: Returns a task ID for tracking the processing status.
    - `400 Bad Request`: Invalid file type or empty file.

### Check Status
- **Endpoint:** `/status/<task_id>`
- **Method:** `GET`
- **Description:** Check the status of the CSV processing task.
- **Response:**
    - `200 OK`: Returns the status of the task.
    - `404 Not Found`: Task ID not found.

### Get Processed Images
- **Endpoint:** `/processed_images/<filename>`
- **Method:** `GET`
- **Description:** Retrieve processed images from the specified CSV file.
- **Response:**
    - `200 OK`: Returns the processed images.
    - `500 Internal Server Error`: Error retrieving processed images.
