import datetime
import decimal
import typing
import uuid
from enum import Enum

from readstr.base64 import base64_decode

_READERS = {}


# noinspection PyShadowingBuiltins
def reads_generic(type):
    def decorator(func):
        _READERS[type] = func
        return func

    return decorator


def reads(func):
    typehints = typing.get_type_hints(func)
    returns = typehints['return']
    return reads_generic(returns)(func)


@reads
def read_uuid(str_value: str) -> uuid.UUID:
    try:
        return uuid.UUID(str_value)
    except ValueError:
        pass
    try:
        return uuid.UUID(bytes=base64_decode(str_value))
    except ValueError:
        pass
    raise ValueError('not a UUID in any recognized format')


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
def read_tuple(str_value: str, args) -> tuple:
    return tuple((readstr(arg_value, arg_type) for arg_value, arg_type in zip(str_value.split(','), args)))


@reads
def read_dict(str_value: str, args) -> dict:
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


@reads
def read_list(str_value: str, args: tuple) -> list:
    result = list()
    arg_type, = args
    for v in str_value.split(','):
        result.append(readstr(v, arg_type))
    return result


@reads
def read_set(str_value: str, args: tuple) -> set:
    result = set()
    arg_type, = args
    for v in str_value.split(','):
        result.add(readstr(v, arg_type))
    return result


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
    raise ValueError(f'no way to convert into {target}: "{str_value}"')
