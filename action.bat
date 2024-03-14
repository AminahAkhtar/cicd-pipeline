@echo off
set UPLOAD_FLAG=false

rem Check if the UPLOAD_FLAG environment variable is set
if "%UPLOAD_FLAG%"=="true" (
    rem Copy large file to S3
    aws s3 cp classifier\app\api\classifier\VGG16_custom\variables\variables.data-00000-of-00001 s3://bestskills/large-files/variables.data-00000-of-00001
    echo File uploaded to S3.
) else (
    echo File upload skipped. Set UPLOAD_FLAG=true to enable.
)
