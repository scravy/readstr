import base64
from typing import Union

_tt = bytes.maketrans(b'-_', b'+/')


def base64_decode(base64_encoded: Union[str, bytes]) -> bytes:
    actual_length = len(base64_encoded)
    missing_padding = 4 - (actual_length % 4)
    if isinstance(base64_encoded, str):
        base64_encoded = base64_encoded.encode('ascii')
    base64_encoded = base64_encoded.translate(_tt)
    if missing_padding % 4:
        base64_encoded = base64_encoded + (b'=' * missing_padding)
    return base64.b64decode(base64_encoded)
