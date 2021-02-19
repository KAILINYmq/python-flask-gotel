import logging

import boto3
import s3fs
import time
from botocore.exceptions import ClientError

from agile.config import *

local_tmp_dir = '/tmp'


class S3Provider:
    expire_s = 2400

    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None, profile_name=None, role_arn=None,
                 region='cn-north-1'):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.profile_name = profile_name
        self.role_arn = role_arn
        self.region = region
        self.session = None
        self.resource = None
        self.fs = None
        self.ts = None

    def __check_expire(self):
        if not self.ts or time.time() - self.ts > S3Provider.expire_s:
            self.init_session()

    def init_session(self):
        self.session = self.create_session()
        self.resource = self.session.resource('s3')
        credentials = self.session.get_credentials()
        self.fs = s3fs.S3FileSystem(key=credentials.access_key, secret=credentials.secret_key,
                                    token=credentials.token, client_kwargs={'region_name': self.region})
        self.ts = time.time()
        return self

    def create_session(self):
        if self.role_arn:
            sts_client = boto3.client('sts')
            assumed_role_object = sts_client.assume_role(
                RoleArn=self.role_arn,
                RoleSessionName="AssumeRoleSession1"
            )
            credentials = assumed_role_object['Credentials']
            return boto3.Session(aws_access_key_id=credentials['AccessKeyId'],
                                 aws_secret_access_key=credentials['SecretAccessKey'],
                                 aws_session_token=credentials['SessionToken'],
                                 region_name=self.region)
        if self.profile_name:
            return boto3.Session(aws_access_key_id=self.aws_access_key_id,
                                 aws_secret_access_key=self.aws_secret_access_key,
                                 profile_name=self.profile_name,
                                 region_name=self.region)
        if self.aws_access_key_id and self.aws_secret_access_key:
            return boto3.Session(aws_access_key_id=self.aws_access_key_id,
                                 aws_secret_access_key=self.aws_secret_access_key,
                                 region_name=self.region)
        return boto3.Session(region_name=self.region)

    def get_session(self):
        self.__check_expire()
        return self.session

    def get_resource(self):
        self.__check_expire()
        return self.resource

    def get_fs(self):
        self.__check_expire()
        return self.fs

    def clone(self):
        return S3Provider(self.aws_access_key_id, self.aws_secret_access_key, self.profile_name, self.role_arn)


class Bucket:
    def __init__(self, s3_provider, bucket_name):
        self.s3_provider = s3_provider
        self.bucket_name = bucket_name

    @property
    def bucket(self):
        return self.s3_provider.get_resource().Bucket(self.bucket_name)

    def clone(self):
        return Bucket(self.s3_provider.clone(), self.bucket_name)

    def object(self, obj_key):
        return self.s3_provider.get_resource().Object(self.bucket_name, obj_key)

    def objects(self, prefix=None, skip_folder=True):
        if not prefix:
            results = self.bucket.objects.all()
        else:
            results = self.bucket.objects.filter(Prefix=prefix)
        if not skip_folder:
            return results
        return [result for result in results if not skip_folder or not result.key.endswith('$folder$')]

    def exists(self, obj_key):
        try:
            self.object(obj_key).load()
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                raise

    def form_url(self, obj_key):
        return 's3://{}/{}'.format(self.bucket_name, obj_key)

    def open_s3fs(self, obj_key, mode='rb'):
        return self.s3_provider.get_fs().open('s3://{}/{}'.format(self.bucket_name, obj_key), mode=mode)

    def read(self, obj_key):
        with self.open_s3fs(obj_key) as f:
            return f.read()

    def write(self, obj_key, byte_array):
        with self.open_s3fs(obj_key, 'wb') as f:
            f.write(byte_array)

    def download(self, obj_key, local_file):
        os.makedirs(os.path.split(local_file)[0], exist_ok=True)
        with open(local_file, 'wb') as f:
            self.bucket.download_fileobj(obj_key, f)

    def download_all(self, prefix, local_dir, local_prefix=''):
        os.makedirs(local_dir, exist_ok=True)
        for obj in self.objects(prefix):
            file_name = obj.key.split('/')[-1]
            self.download(obj.key, local_dir + '/{}{}'.format(local_prefix, file_name))

    def upload(self, local_file, obj_key):
        if os.path.isfile(local_file):
            with open(local_file, 'rb') as f:
                self.object(obj_key).put(Body=f)
        else:
            if not obj_key.endswith('/'):
                obj_key += '/'
            for root, dirs, files in os.walk(local_file):
                for file in files:
                    file_path = root + '/' + file
                    rel_file_path = file_path[len(local_file):]
                    if rel_file_path.startswith('/'):
                        rel_file_path = rel_file_path[1:]
                    target_obj_key = obj_key + rel_file_path
                    with open(file_path, 'rb') as f:
                        self.object(target_obj_key).put(Body=f)

    def delete(self, obj_key):
        self.bucket.object(obj_key).delete()

    def generate_presigned_url(self, obj_key, expiration=86400):
        s3_client = self.bucket.meta.client
        try:
            return s3_client.generate_presigned_url('get_object', Params={
                'Bucket': self.bucket_name,
                'Key': obj_key
            }, ExpiresIn=expiration)

        except ClientError as e:
            logging.error(e)
        return None


DEFAULT_S3_PROVIDER = S3Provider(S3_SECRET_KEY_ID, S3_SECRET_ACCESS_KEY, region=S3_REGION)
DEFAULT_BUCKET = Bucket(DEFAULT_S3_PROVIDER, S3_BUCKET_NAME)

if __name__ == '__main__':
    obj = DEFAULT_BUCKET.object('PackageAI/dataset/sku_list.json')
    print(obj)
