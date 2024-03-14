from fastapi import APIRouter, UploadFile, File, Header, Depends, HTTPException
import os
import shutil
import boto3
import botocore
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
    return {"message": "svc_file_handler service 0.1 alive devops"}

# Function to list all files in the S3 bucket
def list_files():
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    S3_BUCKET_NAME = os.getenv("BUCKET_NAME")
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME)
    files = [obj['Key'] for obj in response.get('Contents', [])]
    return files

@router.get("/")
async def get_files():
    try:
        print("file.handler.api./")
        files = list_files()
        return {"files": files}
    except botocore.exceptions.EndpointConnectionError as e:
        return {"error": f"Error connecting to the S3 endpoint: {str(e)}"}
    except botocore.exceptions.ClientError as e:
        return {"error": f"S3 client error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
