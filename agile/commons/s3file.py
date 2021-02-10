# coding: utf-8
""" upload file onto amazon s3
"""

import logging
import time

import boto3
from botocore.exceptions import ClientError
BUCKET_NAME = 'aws-ul-dh-cmi-bi-prd-bj-s3'

def upload_file(file_name, bucket='aws-ul-dh-cmi-bi-prd-bj-s3', object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    base_dir = '/innoflex/logo/'
    if object_name is None:
        object_name = base_dir+file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)

    except ClientError as e:
        logging.error(e)
        return False
    return True


def download_file():
    s3 = boto3.client('s3')
    s3.download_file('aws-ul-dh-cmi-bi-prd-bj-s3', '11.txt', '11.txt')


def create_presigned_url(file_name, expiration=86400):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    base_dir = '/innoflex/logo/'
    object_name = base_dir + file_name

    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': BUCKET_NAME,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)

    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


def test():
    key = "11.txt"
    location = boto3.client('s3').get_bucket_location(Bucket='aws-ul-dh-cmi-bi-prd-bj-s3')['LocationConstraint']

    url = "https://s3-%s.amazonaws.com/%s/%s" % (location, 'aws-ul-dh-cmi-bi-prd-bj-s3', key)


def get_wensite():
    s3 = boto3.client('s3')

    result = s3.get_bucket_website(Bucket='aws-ul-dh-cmi-bi-prd-bj-s3')


def del_object(file_names):
    s3 = boto3.client('s3')
    Objects_list  = list()
    for index in range(len(file_names)):
        Objects_list.append({
            'Key': file_names[index]
        })
        if len(Objects_list)==100:
            ff = s3.delete_objects(Bucket='aws-ul-dh-cmi-bi-prd-bj-s3',Delete={
                'Objects': Objects_list
            })
            Objects_list = []






if __name__ == '__main__':
    # upload_file('11.txt', 'aws-ul-dh-cmi-bi-prd-bj-s3')
    # download_file()
    # a = create_presigned_url('aws-ul-dh-cmi-bi-prd-bj-s3', 'brandlogo_2149373.gif')
    # print(a)
    # get_wensite()
    # test()
    # upload_website('aws-ul-dh-cmi-bi-prd-bj-s3', 'html', 'index.html')
    del_object([])
