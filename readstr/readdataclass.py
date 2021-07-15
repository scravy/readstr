import dataclasses
import os
import sys
from itertools import zip_longest
from typing import TypeVar, Type, Callable, Optional, List

from readstr import readstr

T = TypeVar('T')


class ReadException(Exception):
    pass


def args_as_env(argv: List[str] = sys.argv):
    skip = False
    env = dict()
    for arg, arg_value in zip_longest(argv[1:], argv[2:], fillvalue=None):
        if skip:
            skip = False
            continue
        key: str
        if arg.startswith('--'):
            key = arg[2:]
        elif arg.startswith('-'):
            key = arg[1:]
        else:
            continue
        if '=' in key:
            key, arg_value = key.split('=', maxsplit=1)
        else:
            skip = True
        env[key.translate(str.maketrans({'-': '_'})).upper()] = arg_value
    return env


def from_env(t: Type[T], getenv: Callable[[str], Optional[str]] = os.environ.get) -> T:
    """
    Read a dataclass from environment variables.

    :param t: A dataclass type
    :param getenv: A function that allows retrieving environment variables by name and defaults to None
    :return: An instance of `t`
    """
    values = dict()
    missing = dict()
    errors = dict()
    for field in dataclasses.fields(t):
        env_name = field.name.upper()
        value = getenv(env_name)
        if value is None:
            if field.default_factory is dataclasses.MISSING:
                if field.default is dataclasses.MISSING:
                    missing[env_name] = field
                    continue
                else:
                    value = field.default
            else:
                value = field.default_factory()
        else:
            try:
                value = readstr(value, field.type)
            except ValueError as exc:
                errors[env_name] = exc
                continue
        values[field.name] = value

    messages = []
    if missing:
        messages.append(f"missing required config for {', '.join(sorted(missing.keys()))}")
    for env_name, exc in errors.items():
        messages.append(f"invalid value for {env_name}: {exc}")
    if messages:
        raise ReadException('; '.join(messages))

    return t(**values)


def otherwise(value, fallback):
    if value is None:
        return fallback()
    return value


def from_env_or_args(t: Type[T],
                     getenv: Callable[[str], Optional[str]] = os.environ.get,
                     argv: List[str] = sys.argv) -> T:
    """
    Read a dataclass from environment variables or from command line arguments.

    Command line arguments override environment variables.

    Given a dataclass:

    @dataclass
    class Config:
        key: str

    The following invocations of `some.py` will read the same `Config` object:

    KEY=value ./some.py
    ./some.py --key value
    ./some.py --key=value
    ./some.py -key value
    ./some.py -key=value
    export KEY=value; ./some.py
    """
    args_env = args_as_env(argv)
    return from_env(t, lambda k: otherwise(args_env.get(k), lambda: getenv(k)))
