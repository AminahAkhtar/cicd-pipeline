from fastapi import APIRouter, HTTPException, Header, Depends
import boto3
import jwt
import botocore
import os
from typing import List

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

def delete_file_and_chunks(file_name: str):
    try:
        # Delete the main file
        s3.delete_object(Bucket=S3_BUCKET_NAME, Key=file_name)

        # Delete all chunks associated with the file
        response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix=f"largefiles/{file_name}")
        for obj in response.get('Contents', []):
            obj_key = obj['Key']
            s3.delete_object(Bucket=S3_BUCKET_NAME, Key=obj_key)
    except botocore.exceptions.ClientError as e:
        raise HTTPException(status_code=500, detail=f"S3 client error: {str(e)}")

@router.delete("/{file_name}")
async def delete_file(file_name: str):
    try:
        delete_file_and_chunks(file_name)
        return {"message": f"File '{file_name}' and its associated chunks deleted successfully."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
