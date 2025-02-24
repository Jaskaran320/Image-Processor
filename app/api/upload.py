from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
import csv
from app.services.csv_processing import validate_csv_format
from app.tasks.image_tasks import process_all_products_task
from app.core.database import get_db_connection
import sqlite3

router = APIRouter()

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_csv_file(
    csv_file: UploadFile = File(...),
    webhook_url: Optional[str] = Form(None),
    db: sqlite3.Connection = Depends(get_db_connection)
):
    if not csv_file:
        raise HTTPException(status_code=400, detail="No CSV file part")
    if csv_file.filename == '':
        raise HTTPException(status_code=400, detail="No selected CSV file")
    if not csv_file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    csv_content = await csv_file.read()
    is_valid_format, error_message = validate_csv_format(csv_content)
    if not is_valid_format:
        raise HTTPException(status_code=400, detail=error_message)

    request_id = str(uuid.uuid4())
    filename = f"uploaded_csv_{request_id}.csv"
    csv_filepath = f"app/uploads/{filename}"
    with open(csv_filepath, "wb") as f:
        f.write(csv_content)

    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO requests (request_id, csv_filename, status, webhook_url)
        VALUES (?, ?, ?, ?)
    ''', (request_id, filename, 'PENDING', webhook_url))
    db.commit()

    csv_text = csv_content.decode('utf-8')
    products_data = list(csv.reader(csv_text.splitlines()))[1:] # Skip header

    for row in products_data:
        serial_number, product_name, input_image_urls = row
        cursor.execute('''
            INSERT INTO products (request_id, serial_number, product_name, input_image_urls, processing_status)
            VALUES (?, ?, ?, ?, ?)
        ''', (request_id, serial_number, product_name, input_image_urls, 'PENDING'))
    db.commit()

    process_all_products_task.delay(request_id, products_data)

    return JSONResponse(
        status_code=202,
        content={'request_id': request_id, 'message': 'CSV uploaded successfully. Processing started. (via Celery)'}
    )