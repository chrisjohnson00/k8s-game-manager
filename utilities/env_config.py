import os


def get_config(key):
    """
    Get the env var value if it exists, else raise a KeyError.  Use this for required env values.
    :param key: The env var key to lookup
    :return: str
    """
    if os.environ.get(key):
        return os.environ.get(key)
    raise KeyError(f"{key} was not found as an env var")


def get_config_with_default(key, default):
    """
    Get the env var value if it exists, else return default.  Use this for optional env values.
    :param key: The env var key to lookup
    :param default: The value to use if the env var isn't set
    :return: str
    """
    try:
        return get_config(key)
    except KeyError:
        return default
