from fastapi import FastAPI
from api.filer.list import router as list
from api.filer.upload import router as upload
from api.filer.download import router as download
from api.filer.search import router as search
from api.filer.streamup import router as streamup
from api.filer.streamdown import router as streamdown
from api.filer.delete import router as delete
# from starlette.middleware import MultipartMiddleware


from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

# Retrieve CORS URLs from environment variables
cors_urls = os.getenv("urls", "").split(",")

app = FastAPI(openapi_url="/api/v1/file/openapi.json", docs_url="/api/v1/file/docs")


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_urls,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Adjust the maximum file size allowed for uploads (in bytes)
# app.add_middleware(MultipartMiddleware, max_upload_size=1024 * 1024 * 1024)  # Allow up to 1GB uploads

app.include_router(list, prefix="/api/v1/list", tags=["list"])
app.include_router(upload, prefix="/api/v1/upload", tags=["upload"])
app.include_router(download, prefix="/api/v1/download", tags=["download"])
app.include_router(search, prefix="/api/v1/search", tags=["search"])
app.include_router(streamup, prefix="/api/v1/streamup", tags=["streamup"])
app.include_router(streamdown, prefix="/api/v1/streamdown", tags=["streamdown"])
app.include_router(delete, prefix="/api/v1/delete", tags=["delete"])


