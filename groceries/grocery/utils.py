import boto3
import uuid
from django.conf import settings

def get_s3_client():
    """
    Create and return a boto3 S3 client using credentials from your Django settings.
    """
    return boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

def upload_image_to_s3(file_obj, folder="grocery_items"):
    # Generate a unique filename using UUID and preserve the file extension.
    extension = file_obj.name.split('.')[-1]
    file_key = f"{folder}/{uuid.uuid4()}.{extension}"
    
    s3_client = get_s3_client()
    try:
        s3_client.upload_fileobj(
            file_obj,
            settings.AWS_STORAGE_BUCKET_NAME,
            file_key,
            ExtraArgs={
                "ACL": "public-read",  # Make the file publicly accessible.
                "ContentType": file_obj.content_type
            }
        )
    except Exception as e:
        print("Error uploading file to S3:", e)
        return None
    
    # Return the URL constructed using your custom domain.
    return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_key}"

def get_image_url(file_key):
    """
    Given an S3 file key, return the public URL for the object.
    
    Parameters:
      file_key: The S3 key for the file.
      
    Returns:
      The public URL string to access the file.
    """
    return f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_key}"

def delete_image_from_s3(file_key):
    """
    Delete an image from the AWS S3 bucket.
    
    Parameters:
      file_key: The S3 key for the file to delete.
      
    Returns:
      True if deletion was successful, False otherwise.
    """
    s3_client = get_s3_client()
    try:
        s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)
    except Exception as e:
        print("Error deleting file from S3:", e)
        return False
    return True
