import os


def env_str(key: str, default: str | None = None) -> str | None:
    """
    Reads env variable and converts it to str

    :param key: env variable name
    :param default: default value
    :return: converted env variable or default value
    """

    v = os.getenv(key)
    return v if (v is not None and v.strip() != "") else default

def env_int(key: str, default: int) -> int:
    """
       Reads env variable and converts it to int

       :param key: env variable name
       :param default: default value
       :return: converted env variable or default value
       """

    v = env_str(key)
    if v is None:
        return default
    try:
        return int(v)
    except ValueError as e:
        raise ValueError(f"{key} must be an integer, got: {v!r}") from e
