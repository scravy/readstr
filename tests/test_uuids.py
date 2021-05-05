import unittest
import uuid

from readstr import readable_uuid, read_uuid


class UuidTestCase(unittest.TestCase):
    def test_read_uuid(self):
        uuid_ = uuid.uuid4()
        readable = readable_uuid(uuid_)
        self.assertEqual(22, len(readable))
        self.assertEqual(uuid_, read_uuid(readable))


if __name__ == '__main__':
    unittest.main()
