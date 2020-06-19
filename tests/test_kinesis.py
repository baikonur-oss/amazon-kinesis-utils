import base64
import unittest

from amazon_kinesis_utils import kinesis


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
        data = "plain text record sample"
        data_blob = data.encode()
        data_base64 = base64.b64encode(data_blob)

        event = {
            "Records": [
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
            ]
        }

        records = [x for x in kinesis.parse_records(event["Records"])]

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], data)
