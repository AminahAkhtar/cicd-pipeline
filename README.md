## Service Description

This service exposes APIs that list, upload, and download files from the S3 bucket. The service is designed to work seamlessly with Docker for easy deployment.

## Features

- **JWT Authentication**: Secure routes with JWT (JSON Web Tokens).
- **AWS S3 Integration**: Store and retrieve files from AWS S3.

## Getting Started

To get started with this project, clone the repository and build the docker-compose.

### Prerequisites
- Docker

### Installation

1. Clone the repository:
   ```bash
   git clone [your-repo-link]
   ```
2. Build docker-compose:
   ```bash
   docker-compose build
   ```

## Usage

### JWT Authentication

Secure your endpoints using JWT. The token is required in the header of the requests. for token call the UserAuth service.

### API Endpoints

1. **List Files in S3 Bucket**
   - **GET** `http://0.0.0.0:8005/api/v1/list`
   - Lists all files stored in the configured S3 bucket.

2. **Upload File to S3 Bucket**
   - **POST** `http://0.0.0.0:8005/api/v1/upload`
   - Allows file uploading to the S3 bucket.

3. **Search File from S3 Bucket**
   - **GET** `http://0.0.0.0:8005/api/v1/search?query='keyword'`
   - lists matched file from the S3 bucket.

## Configuration

Set up your AWS credentials and other configurations in the `.env` file.

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `BUCKET_NAME`

