import unittest
from utilities.file_name_security import safe_file_name


class TestSafeFileName(unittest.TestCase):

    def test_valid_file_name(self):
        result = safe_file_name("file.txt")
        self.assertTrue(result)

    def test_invalid_file_name(self):
        with self.assertRaises(ValueError):
            safe_file_name("../file.txt")
