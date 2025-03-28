import boto3
import uuid
from django.conf import settings

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

def upload_image_to_s3(file_obj, folder="grocery_items"):
    extension = file_obj.name.split('.')[-1]
    file_key = f"{folder}/{uuid.uuid4()}.{extension}"
    s3_client = get_s3_client()
    try:
        s3_client.upload_fileobj(
            file_obj,
            settings.AWS_STORAGE_BUCKET_NAME,
            file_key,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": file_obj.content_type
            }
        )
    except Exception as e:
        print("Error uploading file:", e)
        return None
    return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_key}"

def delete_image_from_s3(file_key):
    s3_client = get_s3_client()
    try:
        s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)
    except Exception as e:
        print("Error deleting file:", e)
        return False
    return True
