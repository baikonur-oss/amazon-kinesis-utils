import base64
import gzip
import logging
import random
import string
import time
from json import JSONDecodeError, loads
from typing import List, Generator

from aws_kinesis_agg.deaggregator import iter_deaggregate_records

from .misc import split_list

logger = logging.getLogger("kinesis_logging_utils")
logger.setLevel(logging.INFO)


class KinesisException(Exception):
    """
    A custom exception returned on put_records_batch failures. Intentionally not catching this exception in Lambda
    Functions (source mapped to a Kinesis Data Stream) will make Lambda rerun until all record are successfully sent.
    """

    pass


def normalize_cloudwatch_messages(payload: str) -> List[str]:
    """
    Normalize messages from CloudWatch Logs subscription filters and pass through other data
    
    :param payload: A string containing JSON data (decoded payload inside Kinesis records)
    :return: List of normalized raw data
             (CloudWatch Logs subscription filters may send multiple log events in one payload)
    """
    # Normalize messages from CloudWatch (subscription filters) and pass through anything else
    # https://docs.aws.amazon.com/ja_jp/AmazonCloudWatch/latest/logs/SubscriptionFilters.html

    logger.debug(f"Normalizer input: {payload}")

    if len(payload) < 1:
        logger.error(f"Got weird record, skipping: {payload}")
        return []

    # check if data is JSON and parse
    try:
        payload_json = loads(payload)
        if type(payload_json) is not dict:
            logger.error(f"Top-level JSON data is not an object, giving up: {payload}")
            return []

    except JSONDecodeError:
        return [payload]

    if "messageType" not in payload_json:
        return [payload]

    # messageType is present in payload, must be coming from CloudWatch
    logger.debug(
        f"Got payload looking like CloudWatch Logs via subscription filters: {payload_json}"
    )

    return extract_data_from_json_cwl_message(payload_json)


def extract_data_from_json_cwl_message(message: dict) -> List[str]:
    """
    Extract log events from CloudWatch Logs subscription filters JSON messages (parsed to dict).
    For details, see: https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/SubscriptionFilters.html 

    :param message: Dictionary representing CloudWatch Logs subscription filters JSON messages
    :return: List of raw log event messages
    """
    if message["messageType"] == "CONTROL_MESSAGE":
        logger.info(f"Got CONTROL_MESSAGE from CloudWatch: {message}, skipping")
        return []

    elif message["messageType"] == "DATA_MESSAGE":
        data = []

        if "logEvents" not in message:
            logger.error(
                f"Got DATA_MESSAGE from CloudWatch Logs but logEvents are not present, "
                f"skipping payload: {message}"
            )
            return []

        events = message["logEvents"]

        for event in events:
            message = event["message"]
            logger.debug(f"message: {message}")

            data.append(message)

        return data

    else:
        logger.error(f"Got unknown messageType: {message['messageType']} , skipping")
        return []


def create_records(data: List[str]) -> List[dict]:
    """
    Create Kinesis Records for use with PutRecords API

    :param data: List of strings to convert to records
    :return: List of Kinesis Records for PutRecords API
    """
    random_alphanumerical = (
        string.ascii_lowercase + string.ascii_uppercase + string.digits
    )

    records = []
    d: str
    for d in data:
        data_blob = d.encode("utf-8")
        partition_key: str = "".join(
            random.choices(random_alphanumerical, k=20)
        )  # max 256 chars
        records.append({"Data": data_blob, "PartitionKey": partition_key})
    logger.debug(f"Formed Kinesis Records batch for PutRecords API: {records}")
    return records


def put_records_batch(
    client, stream_name: str, records: list, max_retries: int, max_batch_size: int = 500
) -> None or List[dict]:
    """
    Put multiple records to Kinesis Data Streams using PutRecords API in batches.

    :param client: Kinesis API client (e.g. boto3.client('kinesis') )
    :param stream_name: Kinesis Data Streams stream name
    :param records: list of records to send. Records will be dumped with json.dumps
    :param max_retries: Maximum retries for resending failed records
    :param max_batch_size: Maximum number of records sent in a single PutRecords API call.
    :return: Records failed to put in Kinesis Data Stream after all retries. Each PutRecords API call can receive up
             to 500 records:
             https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kinesis.html#Kinesis.Client.put_records
    """

    retry_list = []

    for batch_index, batch in enumerate(split_list(records, max_batch_size)):
        records_to_send = create_records(batch)
        retries_left = max_retries

        while len(records_to_send) > 0:
            kinesis_response = client.put_records(
                Records=records_to_send, StreamName=stream_name,
            )

            if kinesis_response["FailedRecordCount"] == 0:
                break
            else:
                index: int
                record: dict
                for index, record in enumerate(kinesis_response["Records"]):
                    if "ErrorCode" in record:
                        # original records list and response record list have same order, guaranteed:
                        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kinesis.html#Kinesis.Client.put_records
                        logger.error(
                            f"A record failed with error: {record['ErrorCode']} {record['ErrorMessage']}"
                        )
                        retry_list.append(records_to_send[index])

                records_to_send = retry_list
                retry_list = []

                if retries_left == 0:
                    error_msg = (
                        f"No retries left, giving up on records: {records_to_send}"
                    )
                    logger.error(error_msg)
                    return records_to_send

                retries_left -= 1

                logger.info(f"Waiting 500 ms before retrying")
                time.sleep(0.5)

    return None


def parse_records(raw_records: list) -> Generator[str, None, None]:
    """
    Generator that de-aggregates, decodes, gzip decompresses Kinesis Records

    :param raw_records: Raw Kinesis records (usually event['Records'] in Lambda handler function)
    :return:
    """
    for record in iter_deaggregate_records(raw_records):
        logger.debug(f"Raw Kinesis record: {record}")

        # Kinesis data is base64 encoded
        raw_data = base64.b64decode(record["kinesis"]["data"])

        # decompress data if raw data is gzip (log data from CloudWatch Logs subscription filters comes gzipped)
        # gzip magic number: 0x1f 0x8b
        if raw_data[0] == 0x1F and raw_data[1] == 0x8B:
            raw_data = gzip.decompress(raw_data)

        data = raw_data.decode()
        payloads = normalize_cloudwatch_messages(data)
        logger.debug(f"Normalized payloads: {payloads}")

        for payload in payloads:
            yield payload
