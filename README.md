# readstr

Provides `readstr`, a function that can read a lot of different types from strings:

```python
from readstr import readstr

readstr('1,2,3', typing.Set[int])
readstr('foo=3,bar=10', typing.Dict[str, int])
readstr('vUfDOuQwRVavn3_QjMxp7Q', uuid.UUID)
```

Useful for reading arguments from command line arg, from environment variables, etc.
