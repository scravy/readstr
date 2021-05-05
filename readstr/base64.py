import base64
from typing import Union


# noinspection PyIncorrectDocstring
def base64_decode(base64_encoded: Union[str, bytes], *, _tt=bytes.maketrans(b'-_', b'+/')) -> bytes:
    """
    Reads base64 and modified base64, even with missing padding.
    :param base64_encoded: A base64 or modified base64 encoded str or bytes object, with or without padding.
    :return: The decoded bytes.
    """
    actual_length = len(base64_encoded)
    missing_padding = 4 - (actual_length % 4)
    if isinstance(base64_encoded, str):
        base64_encoded = base64_encoded.encode('ascii')
    base64_encoded = base64_encoded.translate(_tt)
    if missing_padding % 4:
        base64_encoded = base64_encoded + (b'=' * missing_padding)
    return base64.b64decode(base64_encoded)
