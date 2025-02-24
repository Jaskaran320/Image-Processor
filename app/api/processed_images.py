from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()
PROCESSED_FOLDER = 'app/processed'

@router.get("/processed_images/{filename}")
async def get_processed_image(filename: str) -> FileResponse:
    filepath = os.path.join(PROCESSED_FOLDER, filename)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(filepath)
