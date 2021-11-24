import collections
import datetime
import decimal
import typing
import uuid
from enum import Enum
from pathlib import Path

from .base64 import base64_decode

_READERS = {}


# noinspection PyShadowingBuiltins
def reads_generic(type):
    def decorator(func):
        _READERS[type] = func
        return func

    return decorator


def reads(func):
    if isinstance(func, type):
        returns = func
    else:
        typehints = typing.get_type_hints(func)
        returns = typehints['return']
    return reads_generic(returns)(func)


@reads
def read_uuid(str_value: typing.Union[str, uuid.UUID]) -> uuid.UUID:
    if not str_value:
        return uuid.UUID('00000000-0000-0000-0000-000000000000')
    if isinstance(str_value, uuid.UUID):
        return str_value
    exceptions = []
    try:
        return uuid.UUID(str_value)
    except (ValueError, TypeError) as exc:
        exceptions.append(exc)
    try:
        return uuid.UUID(bytes=base64_decode(str_value))
    except (ValueError, TypeError) as exc:
        exceptions.append(exc)
    exc_message = ''
    if exceptions:
        exc_message = ', '.join(f"{type(exc).__name}: {exc}" for exc in exceptions)
        exc_message = f' (Errors while processing: {exc_message})'
    raise ValueError(
        f'"{str_value}" (of type {type(str_value).__name__}) is not a UUID in any recognized format{exc_message}')


@reads
def read_str(str_value: str) -> str:
    return str_value


_true_values = {
    'true',
    'yes',
    'on',
    'enable',
    'enabled',
}

_false_values = {
    'false',
    'no',
    'off',
    'disable',
    'disabled',
}


@reads
def read_bool(str_value: str) -> bool:
    try:
        return int(str_value) != 0
    except ValueError:
        pass
    if str_value.lower() in _true_values:
        return True
    if str_value.lower() in _false_values:
        return False
    raise ValueError(f'unrecognized boolean value: {str_value}')


@reads
def read_int(str_value: str) -> int:
    return int(str_value)


@reads
def read_float(str_value: str) -> float:
    return float(str_value)


@reads
def read_complex(str_value: str) -> complex:
    return complex(str_value)


@reads
def read_decimal(str_value: str) -> decimal.Decimal:
    return decimal.Decimal(str_value)


@reads
def read_date(str_value: str) -> datetime.date:
    if str_value.lower() in ('now', 'today'):
        return datetime.date.today()
    if str_value.lower() == 'yesterday':
        return datetime.date.today() - datetime.timedelta(days=1)
    if str_value.lower() == 'tomorrow':
        return datetime.date.today() + datetime.timedelta(days=1)
    return datetime.date.fromisoformat(str_value)


@reads
def read_datetime(str_value: str) -> datetime.datetime:
    if str_value.lower() == 'now':
        return datetime.datetime.now()
    return datetime.datetime.fromisoformat(str_value)


@reads
def read_path(str_value: str) -> Path:
    return Path(str_value)


@reads
def read_tuple(str_value: str, args: tuple) -> tuple:
    result = tuple((readstr(arg_value, arg_type) for arg_value, arg_type in zip(str_value.split(','), args)))
    if len(result) != len(args):
        ValueError(f"not enough values to populate tuple: {str_value} (expected: {len(args)}")
    return result


@reads
def read_bytes(str_value) -> bytes:
    return base64_decode(str_value)


# noinspection PyUnresolvedReferences
@reads_generic(collections.abc.Mapping)
@reads
def read_dict(str_value: str, args: tuple) -> dict:
    key_type, value_type = args
    result = dict()
    for v in str_value.split(','):
        items = v.split('=', 1)
        if len(items) == 2:
            item_key, item_value = items
            key = readstr(item_key, key_type)
            value = readstr(item_value, value_type)
            result[key] = value
    return result


# noinspection PyUnresolvedReferences
@reads_generic(collections.abc.Sequence)
@reads
def read_list(str_value: str, args: tuple) -> list:
    arg_type, = args
    return [readstr(v, arg_type) for v in str_value.split(',')]


# noinspection PyUnresolvedReferences
@reads_generic(collections.abc.Set)
@reads
def read_set(str_value: str, args: tuple) -> set:
    arg_type, = args
    return {readstr(v, arg_type) for v in str_value.split(',')}


@reads
def read_frozenset(str_value: str, args: tuple) -> frozenset:
    arg_type, = args
    return frozenset((readstr(v, arg_type) for v in str_value.split(',')))


@reads_generic(typing.Literal)
def read_literal(str_value: str, args: tuple):
    if str_value in args:
        return str_value
    raise ValueError(f'{str_value} is not any of {args}')


@reads_generic(typing.Union)
def read_union(str_value, args: tuple):
    for arg in args:
        try:
            return readstr(str_value, arg)
        except ValueError:
            pass
    if type(None) in args:
        return None
    raise ValueError(f'{str_value} could not be converted into any of {args}')


def readstr(str_value: str, target):
    if isinstance(target, type) and issubclass(target, Enum):
        # noinspection PyUnresolvedReferences
        enum_value = target.__members__.get(str_value) \
                     or target.__members__.get(str_value.upper()) \
                     or target.__members__.get(str_value.lower())
        if enum_value is not None:
            return enum_value
    if target in _READERS:
        return _READERS[target](str_value)
    origin = typing.get_origin(target)
    if origin is not None and origin in _READERS:
        return _READERS[origin](str_value, typing.get_args(target))
    try:
        return target(str_value)
    except Exception:
        raise ValueError(f'no way to convert into {target}: "{str_value}"')
