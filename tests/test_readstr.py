import datetime
import typing
import unittest
import uuid
from enum import Enum
from unittest import skipIf

from readstr import readstr

no_literal = False

try:
    from typing import Literal  # pylint: disable=no-member
except ImportError:
    no_literal = True


    class Literal:
        pass

no_get_args = False

try:
    from typing import get_args  # pylint: disable=no-member
except ImportError:
    no_get_args = True


    def get_args(*args, **kwargs):
        return tuple()

no_get_origin = False

try:
    from typing import get_origin  # pylint: disable=no-member
except ImportError:
    no_get_origin = True


    def get_origin(*args, **kwargs):
        return None


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

    @skipIf(no_get_origin, "no typing.get_origin available in this python version")
    def test_read_list(self):
        self.assertEqual([1, 3, 5], readstr("1,3,5", typing.List[int]))

    @skipIf(no_get_origin, "no typing.get_origin available in this python version")
    def test_read_set(self):
        self.assertEqual({1, 3, 5}, readstr("1,3,3,5", typing.Set[int]))

    def test_read_enum(self):
        self.assertEqual(Shape.DIAMOND, readstr('rhomb', Shape))
        with self.assertRaises(ValueError):
            readstr('rectangle', Shape)

    @skipIf(no_get_origin, "no typing.get_origin available in this python version")
    def test_read_dict(self):
        expected = {
            'a': uuid.UUID('BD47C33A-E430-4556-AF9F-7FD08CCC69ED'),
            'b': uuid.UUID('BD47C33A-E430-4556-AF9F-7FD08CCC69ED'),
        }
        self.assertEqual(
            expected,
            readstr('a=vUfDOuQwRVavn3_QjMxp7Q,b=vUfDOuQwRVavn3_QjMxp7Q==', typing.Dict[str, uuid.UUID]),
        )

    @skipIf(no_literal, "no typing.Literal available in this python version")
    def test_read_literal(self):
        self.assertEqual('foo', readstr('foo', typing.Literal['foo', 'bar']))
        with self.assertRaises(ValueError):
            readstr('qux', typing.Literal['foo', 'bar'])

    @skipIf(no_literal, "no typing.Literal available in this python version")
    def test_read_literal_set(self):
        self.assertEqual({'foo', 'bar'}, readstr('foo,bar', typing.Set[typing.Literal['foo', 'bar', 'qux']]))
        with self.assertRaises(ValueError):
            readstr('foo,bar,quuz', typing.Set[typing.Literal['foo', 'bar', 'qux']])

    @skipIf(no_get_origin, "no typing.get_origin available in this python version")
    def test_read_optional(self):
        self.assertEqual(7, readstr('7', typing.Optional[int]))
        self.assertEqual(None, readstr('fail', typing.Optional[int]))

    @skipIf(no_get_origin, "no typing.get_origin available in this python version")
    def test_read_union(self):
        self.assertEqual(7, readstr('7', typing.Union[int, float]))
        self.assertEqual(7.0, readstr('7.0', typing.Union[int, float]))
        with self.assertRaises(ValueError):
            readstr('fail', typing.Union[int, float])

    @skipIf(no_get_origin, "no typing.get_origin available in this python version")
    def test_read_tuple(self):
        self.assertEqual((1, 'qux'), readstr('1,qux', typing.Tuple[int, str]))
        self.assertEqual((1, 'foo'), readstr('1,foo', typing.Tuple[int, typing.Literal['foo', 'bar']]))
        with self.assertRaises(ValueError):
            self.assertEqual((1, 'qux'), readstr('1,qux', typing.Tuple[int, typing.Literal['foo', 'bar']]))

    def test_read_date(self):
        self.assertEqual(datetime.date(2020, 1, 18), readstr('2020-01-18', datetime.date))


if __name__ == '__main__':
    unittest.main()
