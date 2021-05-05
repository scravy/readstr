import base64
import uuid


def readable_uuid(source: uuid.UUID, *, _tt=str.maketrans('+/', '-_')) -> str:
    """
    Formats the given UUID using modified base64 without padding.

    Returns a string of exactly 22 characters length.
    """
    return base64.b64encode(source.bytes).decode('utf8').translate(_tt).rstrip('=')
