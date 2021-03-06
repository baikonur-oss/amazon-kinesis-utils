import gzip
import io
import logging

logger = logging.getLogger("kinesis_logging_utils")
logger.setLevel(logging.INFO)


def put_str_data(client, bucket: str, key: str, data: str, gzip_compress: bool = False):
    """
    Put str data to S3 bucket with optional gzip compression

    :param client: S3 API client (e.g. boto3.client('s3') )
    :param bucket: S3 bucket name
    :param key: S3 object key
    :param data: Data to save
    :param gzip_compress: Boolean switch to control gzip compression (default = False)
    """
    if gzip_compress:
        # gzip and put data to s3 in-memory
        data_p = gzip.compress(data.encode(), compresslevel=9)
    else:
        data_p = data.encode()

    with io.BytesIO(data_p) as fileobj:
        s3_results = client.upload_fileobj(fileobj, bucket, key)

    logger.info(f"S3 upload errors: {s3_results}")
