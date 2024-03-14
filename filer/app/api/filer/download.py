from fastapi import APIRouter, Header, HTTPException, Depends, Response
from fastapi.responses import StreamingResponse
import os
import boto3
import jwt
import io

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

# Function to download a file from S3
def download_file(file_key: str):
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    S3_BUCKET_NAME = os.getenv("BUCKET_NAME")


    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    s3_key = f'largefiles/{file_key}'
    response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
    file_data = response['Body'].read()

    # Set content disposition headers to prompt download
    content_type = response['ContentType']
    headers = {
        "Content-Disposition": f'attachment; filename={file_key}',
        "Content-Type": content_type,
    }

    return StreamingResponse(io.BytesIO(file_data), headers=headers)

# Route to download a file from S3

@router.get("/{file_key}")
async def download_file_handler(
    file_key: str
):
    return download_file(file_key)
    