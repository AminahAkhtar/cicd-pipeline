from fastapi import APIRouter, HTTPException, Header, Depends
from typing import List
import boto3
from io import BytesIO
from fastapi.responses import StreamingResponse
import botocore
import os
import mimetypes
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

# AWS credentials and S3 client
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("BUCKET_NAME")

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

def download_file(file_name: str) -> bytes:
    # Retrieve all chunks corresponding to the file
    file_chunks = []
    response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=f"largefiles/{file_name}")
    for obj in response.get('Contents', []):
        obj_key = obj['Key']
        # Fetch the chunk from S3
        obj_data = s3.get_object(Bucket=S3_BUCKET_NAME, Key=obj_key)['Body'].read()
        file_chunks.append(obj_data)
        
    
    # Combine the chunks into a single file
    combined_file = b''.join(file_chunks)
    return combined_file

@router.get("/{file_name}")
async def download_chunked_file(file_name: str):
    try:
        file_content = download_file(file_name)
        if not file_content:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get file extension
        file_extension = os.path.splitext(file_name)[1]

        # Guess mime type based on extension
        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type is None:
            mime_type = 'application/octet-stream'  # Default to binary if MIME type is not recognized
        
        # Prepare response to stream the file
        return StreamingResponse(BytesIO(file_content), media_type=mime_type, headers={"Content-Disposition": f"attachment;filename={file_name}"})
    
    except botocore.exceptions.EndpointConnectionError as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to the S3 endpoint: {str(e)}")
    except botocore.exceptions.ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 client error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
