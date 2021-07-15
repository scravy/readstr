import collections
import datetime
import sys
import typing
import unittest
import uuid
from dataclasses import dataclass
from enum import Enum
from unittest import skipIf

from readstr import readstr
from readstr.readstr import reads


class Shape(Enum):
    SQUARE = 1
    DIAMOND = 2
    CIRCLE = 3
    RHOMB = 2


class ReadStrTestCase(unittest.TestCase):
    def test_read_uuid(self):
        expected = uuid.UUID('BD47C33A-E430-4556-AF9F-7FD08CCC69ED')
        self.assertEqual(expected, readstr('BD47C33A-E430-4556-AF9F-7FD08CCC69ED', uuid.UUID))
        self.assertEqual(expected, readstr('vUfDOuQwRVavn3_QjMxp7Q', uuid.UUID))
        self.assertEqual(expected, readstr('vUfDOuQwRVavn3_QjMxp7Q==', uuid.UUID))

    def test_read_list(self):
        self.assertEqual([1, 3, 5], readstr("1,3,5", typing.List[int]))

    def test_read_set(self):
        self.assertEqual({1, 3, 5}, readstr("1,3,3,5", typing.Set[int]))

    def test_read_enum(self):
        self.assertEqual(Shape.DIAMOND, readstr('rhomb', Shape))
        with self.assertRaises(ValueError):
            readstr('rectangle', Shape)

    def test_read_dict(self):
        expected = {
            'a': uuid.UUID('BD47C33A-E430-4556-AF9F-7FD08CCC69ED'),
            'b': uuid.UUID('BD47C33A-E430-4556-AF9F-7FD08CCC69ED'),
        }
        self.assertEqual(
            expected,
            readstr('a=vUfDOuQwRVavn3_QjMxp7Q,b=vUfDOuQwRVavn3_QjMxp7Q==', typing.Dict[str, uuid.UUID]),
        )

    def test_read_literal(self):
        self.assertEqual('foo', readstr('foo', typing.Literal['foo', 'bar']))
        with self.assertRaises(ValueError):
            readstr('qux', typing.Literal['foo', 'bar'])

    def test_read_literal_set(self):
        self.assertEqual({'foo', 'bar'}, readstr('foo,bar', typing.Set[typing.Literal['foo', 'bar', 'qux']]))
        with self.assertRaises(ValueError):
            readstr('foo,bar,quuz', typing.Set[typing.Literal['foo', 'bar', 'qux']])

    def test_read_optional(self):
        self.assertEqual(7, readstr('7', typing.Optional[int]))
        self.assertEqual(None, readstr('fail', typing.Optional[int]))

    def test_read_union(self):
        self.assertEqual(7, readstr('7', typing.Union[int, float]))
        self.assertEqual(7.0, readstr('7.0', typing.Union[int, float]))
        with self.assertRaises(ValueError):
            readstr('fail', typing.Union[int, float])

    def test_read_tuple(self):
        self.assertEqual((1, 'qux'), readstr('1,qux', typing.Tuple[int, str]))
        self.assertEqual((1, 'foo'), readstr('1,foo', typing.Tuple[int, typing.Literal['foo', 'bar']]))
        with self.assertRaises(ValueError):
            self.assertEqual((1, 'qux'), readstr('1,qux', typing.Tuple[int, typing.Literal['foo', 'bar']]))

    def test_read_date(self):
        self.assertEqual(datetime.date(2020, 1, 18), readstr('2020-01-18', datetime.date))

    def test_extensibility(self):
        @reads
        def read_specialized_dict(str_value: str) -> typing.Dict[str, int]:
            import json
            return json.loads(str_value)

        self.assertEqual({
            'foo': 100,
            'bar': 200,
        }, readstr('{"foo": 100, "bar": 200}', typing.Dict[str, int]))

        @dataclass
        @reads
        class Foo:
            bar: str

        self.assertEqual(Foo('meow'), readstr('meow', Foo))

    def test_sequence(self):
        value = '1,2,3'
        expected = [1, 2, 3]
        self.assertEqual(expected, readstr(value, typing.Sequence[int]))

    @skipIf(sys.version_info < (3, 10), "abc supports generics only from 3.10+")
    def test_sequence_abc(self):
        value = '1,2,3'
        expected = [1, 2, 3]
        self.assertEqual(expected, readstr(value, typing.Sequence[int]))

    def test_mapping(self):
        value = 'foo=3'
        expected = {'foo': 3}
        self.assertEqual(expected, readstr(value, typing.Mapping[str, int]))

    @skipIf(sys.version_info < (3, 10), "abc supports generics only from 3.10+")
    def test_mapping_abc(self):
        value = 'foo=3'
        expected = {'foo': 3}
        # noinspection PyUnresolvedReferences
        self.assertEqual(expected, readstr(value, collections.abc.Mapping[str, int]))

    def test_unknown(self):
        @dataclass(frozen=True)
        class Something:
            value: str

        some_value = 'something'
        self.assertEqual(Something(some_value), readstr(some_value, Something))

    def test_unknown_impossible(self):
        class DoesntWork:
            pass

        some_value = 'something'
        with self.assertRaises(ValueError):
            readstr(some_value, DoesntWork)


if __name__ == '__main__':
    unittest.main()
