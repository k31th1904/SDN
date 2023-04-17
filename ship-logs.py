import os
import boto3
from pathlib import Path

def upload_to_s3(bucket_name, source_directory):
    s3 = boto3.client('s3')

    for file_path in Path(source_directory).glob('*.json'):
        with open(file_path, 'rb') as file:
            key = f'{file_path.name}'
            s3.upload_fileobj(file, bucket_name, key)
            print(f"Uploaded {file_path} to s3://{bucket_name}/{key}")

def main():
    # Set your S3 bucket name and source directory here
    bucket_name = 'flow-logs-sdn'
    source_directory = '/home/ubuntu/SDN/'

    upload_to_s3(bucket_name, source_directory)

if __name__ == '__main__':
    main()
