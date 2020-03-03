import unittest

from amazon_kinesis_utils import misc


class MiscTests(unittest.TestCase):

    def test_list_split(self):
        lst = [x for x in range(100)]

        chunks = misc.split_list(lst, 10)

        chunks_len = 0
        chunks_count = 0
        item_idx = 0

        for chunk in chunks:
            self.assertEqual(len(chunk), 10)
            chunks_len += len(chunk)
            chunks_count += 1

            for item in chunk:
                self.assertEqual(item, lst[item_idx])
                item_idx += 1

        self.assertEqual(chunks_count, 10)
        self.assertEqual(chunks_len, 100)

    def test_dict_default(self):
        d = {
            'a': 'exists'
        }

        self.assertEqual(misc.dict_get_default(d, 'a', None), ('exists', False))
        self.assertEqual(misc.dict_get_default(d, 'b', None), (None, True))
        self.assertEqual(misc.dict_get_default(d, 'b', None, verbose=True), (None, True))


if __name__ == '__main__':
    unittest.main()
