from fastapi import FastAPI
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware

from app.api.upload import router as upload_router
from app.api.status import router as status_router
from app.api.processed_images import router as processed_images_router

FastAPI_HOST = "localhost"
FastAPI_PORT = 8000

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        pass

app = FastAPI(
    lifespan=lifespan,
    title="Image Processor",
    openapi_url=f"/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(status_router)
app.include_router(processed_images_router)

@app.get("/")
async def ping():
    return JSONResponse(content={"ping": "pong!"}, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=FastAPI_HOST,
        port=FastAPI_PORT,
        reload=True,
    )
