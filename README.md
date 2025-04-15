# uuid7-py
This repository provides a single-file drop-in for generating UUID version 7. It is directly sourced from the CPython `uuid` module (with changes introduced in Python 3.14) as outlined in the attached file. It is a **temporary solution** meant for use until Python officially releases a stable version of 3.14.

## Usage
Simply copy the `uuid7.py` file into your project directory and import it as follows:
```
>>> import uuid7 as uuid

>>> uuid.uuid7()
UUID('00976400-be40-7de7-a772-38c88bd11b81')
```

## Attribution and References
This code includes portions of the Python `uuid` module from the CPython source code.
The implementation of UUID version 7 is based on the following commits:
- [Commit 3929af5e3a203291dc07b40c9c3515492e3ba7b4](https://github.com/python/cpython/commit/3929af5e3a203291dc07b40c9c3515492e3ba7b4): Add support for UUID version 7 (RFC 9562)
- [Commit 1121c80fdad1fc1a175f4691f33272cf28a66e83](https://github.com/python/cpython/commit/1121c80fdad1fc1a175f4691f33272cf28a66e83): Improve performance of `UUID.hex` and `UUID.__str__`
- [Commit ba11f45dd969dfb039dfb47270de4f8c6a03d241](https://github.com/python/cpython/commit/ba11f45dd969dfb039dfb47270de4f8c6a03d241): Expose 48-bit timestamp for UUIDv7

For more details, see the following links:
- [RFC 9562](https://www.rfc-editor.org/rfc/rfc9562.html#section-5.7)
- [CPython GitHub - uuid module](https://github.com/python/cpython/blob/main/Lib/uuid.py)

## Disclaimer
This code is provided as a temporary drop-in solution until Python 3.14 is officially released. It is offered "as is" with no warranty — either express or implied. By using this module, you agree that neither the Python Software Foundation nor the repository maintainer will be liable for any damages or other issues arising from its use.

## License
This project is distributed under the Python Software Foundation License. Please refer to the LICENSE file for details.