import base64
import uuid
from typing import Union

from .readstr import read_uuid


def readable_uuid(source: Union[str, uuid.UUID], *, _tt=str.maketrans('+/', '-_')) -> str:
    """
    Formats the given UUID using modified base64 without padding.

    Returns a string of exactly 22 characters length.
    """
    if isinstance(source, str):
        source = read_uuid(source)
    return base64.b64encode(source.bytes).decode('utf8').translate(_tt).rstrip('=')
