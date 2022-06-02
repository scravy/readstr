import dataclasses
import typing as ty
import unittest
import uuid

from readstr.readdataclass import from_env_or_args

from readstr import readstr


@dataclasses.dataclass
class Config:
    platform: ty.Union[uuid.UUID, str, None] = None


class UuidDefaultsTestCase(unittest.TestCase):
    def test_read_uuid_default(self):
        cfg = from_env_or_args(Config, getenv=lambda _: '')
        self.assertEqual(uuid.UUID('00000000-0000-0000-0000-000000000000'), cfg.platform)

    def test_read_uuid_from_empty_string(self):
        value = readstr('', uuid.UUID)
        self.assertEqual(uuid.UUID('00000000-0000-0000-0000-000000000000'), value)

    def test_read_uuid_empty_as_none(self):
        environ = dict(platform='')

        def getenv(key: str) -> ty.Optional[str]:
            if value := environ.get(key):
                return value
        cfg = from_env_or_args(Config, getenv=getenv)
        self.assertEqual(None, cfg.platform)


if __name__ == '__main__':
    unittest.main()
