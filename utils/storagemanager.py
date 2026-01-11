from google.cloud import storage
import os
from datetime import timedelta
storage_client = storage.Client()

def upload_file_to_gcs(file, bucket_name, folder=None):
    bucket = storage_client.bucket(bucket_name)
    path = file.filename
    if folder:
        path = folder + "/" + file.filename
    blob = bucket.blob(path)
    blob.upload_from_file(file)
    # signed_url = blob.generate_signed_url(expiration=timedelta(days=1))
    blob.make_public()
    return blob.public_url