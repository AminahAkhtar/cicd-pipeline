from fastapi import APIRouter, UploadFile, File, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
import os
import boto3
import jwt


# JWT configuration
SECRET_KEY = "Iris-med*tech"
ALGORITHM = "HS256"

def get_current_user(token: str = Header(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")

router = APIRouter()

@router.get("/file")
async def health():
    print("file.handler.api.health")
    return {"message": "svc_file_handler service 0.1 alive"}

# Route to upload a file to S3
@router.post("/")
async def create_upload_file(
    file: UploadFile = File(...)
):
    try:
        AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
        AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
        S3_BUCKET_NAME = os.getenv("BUCKET_NAME")
       

        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

        # Specify the key with the folder name and the file name
        s3_key = f"largefiles/{file.filename}"

        # Upload the file to S3
        s3.upload_fileobj(file.file, S3_BUCKET_NAME, s3_key)

        # Construct the URL for the uploaded file
        file_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"

        return JSONResponse(content={"message": "File uploaded successfully", "file_url": file_url}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))