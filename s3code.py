import boto3


def upload_file(file_name, bucket):
    """Upload a file to s3 bucket"""
    obj_name = file_name
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket, obj_name)

    return response
