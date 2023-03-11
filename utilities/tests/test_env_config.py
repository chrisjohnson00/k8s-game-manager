from utilities.env_config import get_config, get_config_with_default
from unittest import mock
import pytest


def test_get_config():
    with mock.patch.dict('os.environ', {'RDS_MASTER_USERNAME': 'postgres'}):
        assert get_config('RDS_MASTER_USERNAME') == 'postgres'


def test_get_config_not_found():
    with pytest.raises(KeyError):
        get_config('I_DO_NOT_EXIST')


def test_get_config_not_found_with_default():
    with mock.patch.dict('os.environ', {'RDS_MASTER_USERNAME': 'postgres'}):
        assert get_config_with_default('I_DO_NOT_EXIST', 'value') == 'value'
