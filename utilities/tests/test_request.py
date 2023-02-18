import unittest
from unittest.mock import MagicMock
from utilities.request import get_unknown_params


class TestGetUnknownParams(unittest.TestCase):
    def test_get_unknown_params(self):
        # Mock a Flask request object with some POST parameters
        request = MagicMock()
        request.form = {
            'namespace': 'my-namespace',
            'name': 'my-name',
            'param1': 'value1'
        }

        # Define known parameter names
        known_params = ['namespace', 'name']

        # Call get_unknown_params
        unknown_params = get_unknown_params(known_params, request)

        # Check that the correct parameters were extracted
        self.assertEqual(unknown_params, [{'key': 'param1', 'value': 'value1'}])
