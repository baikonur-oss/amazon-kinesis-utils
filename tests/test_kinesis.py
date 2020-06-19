import base64
import json
import unittest
from typing import List, Dict

from amazon_kinesis_utils import kinesis


def generate_sample_kinesis_records(data: list) -> List[Dict]:
    ret = []

    for d in data:
        data_blob = d.encode()
        data_base64 = base64.b64encode(data_blob)
        ret.append(
            {
                "kinesis": {
                    "kinesisSchemaVersion": "1.0",
                    "partitionKey": "0",
                    "sequenceNumber": "00000000000000000000000000000000000000000000000",
                    "data": data_base64,
                    "approximateArrivalTimestamp": 1592558220.000,
                },
                "eventSource": "aws:kinesis",
                "eventVersion": "1.0",
                "eventID": "shardId-000000000000:00000000000000000000000000000000000000000000000",
                "eventName": "aws:kinesis:record",
                "invokeIdentityArn": "arn:aws:iam::000000000000:role/service-role/foo",
                "awsRegion": "ap-northeast-1",
                "eventSourceARN": "arn:aws:kinesis:ap-northeast-1:000000000000:stream/bar",
            }
        )

    return ret


class KinesisTests(unittest.TestCase):
    def test_create_record(self):
        data = "test_data"
        record = kinesis.create_record(data)

        self.assertTrue("Data" in record)
        self.assertTrue("PartitionKey" in record)

        self.assertEqual(record["Data"], b"test_data")

        self.assertTrue(type(record["PartitionKey"]) == str)
        self.assertTrue(len(record["PartitionKey"]) <= 256)

    def test_create_records(self):
        test_data_count = 10
        data_list = [str(x) for x in range(test_data_count)]

        records = kinesis.create_records(data_list)

        for i, record in enumerate(records):
            self.assertTrue("Data" in record)
            self.assertTrue("PartitionKey" in record)

            # ensure same order
            self.assertEqual(record["Data"].decode(), data_list[i])

            self.assertTrue(type(record["PartitionKey"]) == str)
            self.assertTrue(len(record["PartitionKey"]) <= 256)

    def test_parse_records_plaintext(self):
        data = ["plain text record sample"]

        event = {"Records": generate_sample_kinesis_records(data)}

        records = [x for x in kinesis.parse_records(event["Records"])]

        self.assertEqual(len(records), len(data))
        for i, r in enumerate(records):
            self.assertEqual(r, data[i])

    def test_parse_records_plaintext_multiple(self):
        data = [f"test-data-{x}" for x in range(10)]

        event = {"Records": generate_sample_kinesis_records(data)}

        records = [x for x in kinesis.parse_records(event["Records"])]

        self.assertEqual(len(records), len(data))
        for i, r in enumerate(records):
            self.assertEqual(r, data[i])

    def test_parse_records_json_empty(self):
        data = ["{}"]

        event = {"Records": generate_sample_kinesis_records(data)}

        records = [x for x in kinesis.parse_records(event["Records"])]

        self.assertEqual(len(records), len(data))
        for i, r in enumerate(records):
            self.assertEqual(r, data[i])

    def test_parse_records_json_multi(self):
        json_data = [{"a": 1}, {"b": 2}, {"c": 3}]

        data = [json.dumps(x) for x in json_data]

        event = {"Records": generate_sample_kinesis_records(data)}

        records = [x for x in kinesis.parse_records(event["Records"])]

        self.assertEqual(len(records), len(data))
        for i, r in enumerate(records):
            self.assertEqual(r, data[i])

    def test_parse_records_json_root_non_object(self):
        # non-object types on root should be ignored
        data = ["true", "1", "null"]

        event = {"Records": generate_sample_kinesis_records(data)}

        records = [x for x in kinesis.parse_records(event["Records"])]

        self.assertEqual(len(records), 0)
