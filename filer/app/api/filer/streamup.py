from fastapi import APIRouter, File, UploadFile, Header, HTTPException
import boto3
import jwt
import botocore
import os
from typing import List
from io import BytesIO
import asyncio

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

async def upload_chunk_to_s3(chunk_content: bytes, chunk_key: str):
    try:
        s3.upload_fileobj(BytesIO(chunk_content), S3_BUCKET_NAME, chunk_key)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading chunk to S3: {str(e)}")

async def upload_and_combine_chunks(file_chunks: List[bytes], file_name: str):
    try:
        combined_content = b''
        
        combined_url = None

        for i, chunk in enumerate(file_chunks):
           
            chunk_key = f"largefiles/{file_name}_chunk_{i:05}"
            await upload_chunk_to_s3(chunk, chunk_key)

            
            combined_content += chunk

            
            if i == len(file_chunks) - 1:
                combined_key = f"largefiles/{file_name}"
                s3.upload_fileobj(BytesIO(combined_content), S3_BUCKET_NAME, combined_key)
                combined_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{combined_key}"
                

               
                for j in range(len(file_chunks)):
                    chunk_key_to_delete = f"largefiles/{file_name}_chunk_{j:05}"
                    s3.delete_object(Bucket=S3_BUCKET_NAME, Key=chunk_key_to_delete)
                    

                break  

        return combined_url 
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error combining chunks: {str(e)}")

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        
        file_content = await file.read()
        file_size = len(file_content)

        
        if file_size > 100 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size should be less than or equal to 100MB.")

        
        chunk_size = 50 * 1024
        file_chunks = [file_content[i:i+chunk_size] for i in range(0, len(file_content), chunk_size)]

        
        combined_url = await upload_and_combine_chunks(file_chunks, file.filename)

        return {"message": "File uploaded successfully.", "combined_url": combined_url}
    except botocore.exceptions.EndpointConnectionError as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to the S3 endpoint: {str(e)}")
    except botocore.exceptions.ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 client error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
