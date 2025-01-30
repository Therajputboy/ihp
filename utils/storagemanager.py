from google.cloud import storage
import os
from datetime import timedelta
storage_client = storage.Client()

def upload_file_to_gcs(file, bucket_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file.filename)
    blob.upload_from_file(file)
    signed_url = blob.generate_signed_url(expiration=timedelta(days=1))
    return signed_url