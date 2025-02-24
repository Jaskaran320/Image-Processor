import asyncio
import sqlite3
import httpx
import logging
from app.services import image_processing
from app.core.database import DATABASE_NAME
from app.core.celery_app import celery_app

WEBHOOK_URL = 'http://localhost:8000/webhook'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@celery_app.task(name="process_all_products_task")
def process_all_products_task(request_id, products_data):
    asyncio.run(process_all_products_async(request_id, products_data))


async def process_all_products_async(request_id, products_data):
    tasks = [process_product_images_async(request_id, product_data) for product_data in products_data]
    await asyncio.gather(*tasks)


async def process_product_images_async(request_id, product_data):
    serial_number, product_name, input_image_urls_str = product_data
    input_image_urls = [url.strip() for url in input_image_urls_str.split(',')]
    output_image_urls = []

    for index, image_url in enumerate(input_image_urls):
        output_url = await asyncio.to_thread(image_processing.compress_and_upload_image, image_url, product_name, index + 1)
        output_image_urls.append(output_url)

    output_image_urls_str = ",".join([url if url else 'failed' for url in output_image_urls])
    conn = sqlite3.connect(DATABASE_NAME)
    try:
        await update_product_status(request_id, serial_number, output_image_urls_str, conn)
        await check_if_request_complete(request_id, conn)
    finally:
        conn.close()


async def update_product_status(request_id, serial_number, output_image_urls_str, db: sqlite3.Connection):
    cursor = db.cursor()
    cursor.execute('''
        UPDATE products
        SET output_image_urls = ?, processing_status = 'COMPLETED'
        WHERE request_id = ? AND serial_number = ?
    ''', (output_image_urls_str, request_id, serial_number))
    db.commit()


async def check_if_request_complete(request_id, db: sqlite3.Connection):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM products WHERE request_id = ? AND processing_status != 'COMPLETED'", (request_id,))
    pending_products_count = cursor.fetchone()[0]
    if pending_products_count == 0:
        await update_request_status(request_id, 'COMPLETED', db)
        await trigger_webhook(request_id, db)


async def update_request_status(request_id, status, db: sqlite3.Connection):
    cursor = db.cursor()
    cursor.execute('''
        UPDATE requests
        SET status = ?
        WHERE request_id = ?
    ''', (status, request_id))
    db.commit()


async def trigger_webhook(request_id, db: sqlite3.Connection):
    cursor = db.cursor()
    cursor.execute("SELECT webhook_url FROM requests WHERE request_id = ?", (request_id,))
    result = cursor.fetchone()
    webhook_url = result[0] if result else None

    if webhook_url:
        payload = {'request_id': request_id, 'status': 'COMPLETED'}
        headers = {'Content-type': 'application/json'}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(webhook_url, json=payload, headers=headers, timeout=5)
                response.raise_for_status()
                logging.info(f"Webhook triggered successfully for request ID: {request_id} to URL: {webhook_url}, Response: {response.status_code}")
            except httpx.RequestError as e:
                logging.error(f"Webhook request failed for request ID: {request_id} to URL: {webhook_url}, Error: {e}")
            except httpx.HTTPError as e:
                logging.error(f"Webhook HTTP error for request ID: {request_id} to URL: {webhook_url}, Status Code: {e.response.status_code}, Response: {e.response.text}")