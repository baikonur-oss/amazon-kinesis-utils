import base64
import json
import unittest
from typing import List, Dict

from amazon_kinesis_utils import kinesis


def generate_sample_kinesis_records(data: list, encode=True) -> List[Dict]:
    ret = []

    for d in data:
        ret.append(
            {
                "kinesis": {
                    "kinesisSchemaVersion": "1.0",
                    "partitionKey": "0",
                    "sequenceNumber": "00000000000000000000000000000000000000000000000",
                    "data": base64.b64encode(d.encode()) if encode else d,
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

    def test_parse_records_json_multiple(self):
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

    def test_parse_records_cwl_health_check(self):
        # raw sample data from CloudWatch Logs Subscription Filters
        # containing only a health check message:
        # "CWL CONTROL MESSAGE: Checking health of destination Kinesis stream."

        data = [
            "H4sIAAAAAAAAADWOwQqCQBRFf2WYdURGFrkLsRZZQgYtQmLSlz7SGZk3JhH+e6PW8nAv954Pr4BI5HB+18A97kfH8ykKb4cgjje7gE+4ai"
            "XoPilVk7XCpEWocrJBqfKdVk1ts5Fio0FUI1Jzp1RjbVDJLZYGNHHvmgy94AXS9PjhmI11g1bDiMqOOe567i4XznK2ctzJX68XuITsp8d+"
            "eh7zC0ifKHNWgChNwdSDZXYJpeif2R4lEBKjQW3Ku6T7ApsNvwTyAAAA"
        ]

        event = {"Records": generate_sample_kinesis_records(data, encode=False)}

        records = [x for x in kinesis.parse_records(event["Records"])]

        # control messages should be ignored
        self.assertEqual(len(records), 0)

    def test_parse_records_cwl_payload(self):
        # raw sample data from CloudWatch Logs Subscription Filters
        # containing a single DATA_MESSAGE with a plain text payload:
        # "hello"

        data = [
            "H4sIANWN8F4C/02PzQrCMBCE3yVnD83m31vB6slTexORqosG2qYkUZHiu7taBPf47czszsR6TKm9YPMckS3ZqmzKw7aq63JTsQULjwEj4e"
            "JvCHfhsonhNtImY8ozqXPEtp/FRNLtmE7Rj9mHYe27jDGx5W7W77+G6o5D/sCJ+TP5hFJcCQsSLBgHvACtFRRSG2OhMMJyp6RyVmrNrQEt"
            "nDYg4HMse6qR254+4sqB0pIiJBeLXz2Kv2LXBfbav941C5T39AAAAA=="
        ]

        event = {"Records": generate_sample_kinesis_records(data, encode=False)}

        records = [x for x in kinesis.parse_records(event["Records"])]

        self.assertEqual(len(records), 1)

        self.assertEqual(records[0], "hello")

    def test_parse_records_cwl_health_check_payload(self):
        # raw sample data from CloudWatch Logs Subscription Filters
        # containing a single health check and two DATA_MESSAGE payloads
        data = [
            "H4sIAPSW8F4C/6WPzWrDQAyE30VnH7za/9wMdXLKybmVENxWpAu21+xuUkrwu1eJKRRKT9Xxk2ZGc4ORcu7PdPicCTbw1Bya077tumbXQg"
            "XxY6LEuP4xjId43qV4mXlTKJeVdCVRP67HTPLlJb+mMJcQp20YCqUMm+f1/vgQtFeayh3eILyxTmottHSo0KH1KGo0RmOtjLUOayud8Fpp"
            "75Qxwlk00huLEu9hJXCN0o/8kdAetVFsoYSsvuux/TsNQxSwVP+LE3/HqV9xCMtx+QJguUFbZAEAAA==",
            "H4sIAPCW8F4C/zWOwQqCQBRFf2WYdURGFrkLsRZZQgYtQmLSlz7SGZk3JhH+e6PW8nAv954Pr4BI5HB+18A97kfH8ykKb4cgjje7gE+4ai"
            "XoPilVk7XCpEWocrJBqfKdVk1ts5Fio0FUI1Jzp1RjbVDJLZYGNHHvmgy94AXS9PjhmI11g1bDiMqOOe567i4XznK2ctzJX68XuITsp8d+"
            "eh7zC0ifKHNWgChNwdSDZXYJpeif2R4lEBKjQW3Ku6T7ApsNvwTyAAAA",
        ]

        event = {"Records": generate_sample_kinesis_records(data, encode=False)}

        records = [x for x in kinesis.parse_records(event["Records"])]

        self.assertEqual(len(records), 2)

        self.assertEqual(records[0], "hello1")
        self.assertEqual(records[1], "hello2")
