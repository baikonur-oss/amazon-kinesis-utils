import gzip
import unittest

from amazon_kinesis_utils import s3


class MockedS3Client:
    def __init__(self):
        self.uploaded_data = None

    def upload_fileobj(self, fileobj, bucket, key):
        self.uploaded_data = fileobj.read()

    def get_uploaded_data(self):
        return self.uploaded_data


class MiscTests(unittest.TestCase):
    bucket = "bucket-name"
    key = "key-name"
    data = "uncompressed_string_data"

    def test_put_str_data_raw(self):
        s3_client = MockedS3Client()

        s3.put_str_data(
            s3_client, self.bucket, self.key, self.data,
        )

        uploaded_data = s3_client.get_uploaded_data()

        self.assertEqual(type(uploaded_data), bytes)
        self.assertEqual(uploaded_data.decode(), self.data)

    def test_put_str_data_gzipped(self):
        s3_client = MockedS3Client()

        s3.put_str_data(
            s3_client, self.bucket, self.key, self.data, gzip_compress=True,
        )

        uploaded_data = s3_client.get_uploaded_data()

        self.assertEqual(type(uploaded_data), bytes)
        self.assertEqual(gzip.decompress(uploaded_data).decode(), self.data)
