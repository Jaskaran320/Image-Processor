from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from app.core.database import get_db_connection
import sqlite3

router = APIRouter()

@router.get("/status/{request_id}")
async def get_status(request_id: str, db: sqlite3.Connection = Depends(get_db_connection)) -> Dict[str, Any]:
    cursor = db.cursor()
    cursor.execute("SELECT status FROM requests WHERE request_id = ?", (request_id,))
    result = cursor.fetchone()

    if result is None:
        raise HTTPException(status_code=404, detail="Request ID not found")

    status_str = result[0]
    product_statuses = []

    cursor.execute("SELECT serial_number, product_name, processing_status, output_image_urls FROM products WHERE request_id = ?", (request_id,))
    products_data = cursor.fetchall()

    for product in products_data:
        serial_number, product_name, processing_status, output_image_urls = product
        product_statuses.append({
            'serial_number': serial_number,
            'product_name': product_name,
            'processing_status': processing_status,
            'output_image_urls': output_image_urls.split(',') if output_image_urls else []
        })

    return {"request_id": request_id, "status": status_str, "products": product_statuses}
