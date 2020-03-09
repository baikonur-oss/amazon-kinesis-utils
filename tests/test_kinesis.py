import unittest

from amazon_kinesis_utils import kinesis


class KinesisTests(unittest.TestCase):
    def test_create_record(self):
        data = "test_data"
        record = kinesis.create_record(data)

        self.assertTrue('Data' in record)
        self.assertTrue('PartitionKey' in record)

        self.assertEqual(record['Data'], b'test_data')

        self.assertTrue(type(record['PartitionKey']) == str)
        self.assertTrue(len(record['PartitionKey']) <= 256)

    def test_create_records(self):
        test_data_count = 10
        data_list = [str(x) for x in range(test_data_count)]

        records = kinesis.create_records(data_list)

        for i, record in enumerate(records):
            self.assertTrue('Data' in record)
            self.assertTrue('PartitionKey' in record)

            # ensure same order
            self.assertEqual(record['Data'].decode(), data_list[i])

            self.assertTrue(type(record['PartitionKey']) == str)
            self.assertTrue(len(record['PartitionKey']) <= 256)
