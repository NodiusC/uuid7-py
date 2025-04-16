# This file includes portions of the Python `uuid` module.
# The implementation of UUID version 7 is based on the following commits:
# - Commit 3929af5e3a203291dc07b40c9c3515492e3ba7b4: Add support for UUID version 7 (RFC 9562)
# - Commit 1121c80fdad1fc1a175f4691f33272cf28a66e83: Improve performance of `UUID.hex` and `UUID.__str__`
# - Commit ba11f45dd969dfb039dfb47270de4f8c6a03d241: Expose 48-bit timestamp for UUIDv7
# 
# These changes are part of Python 3.14.
# 
# Authors of these changes include:
# - Bénédikt Tran <10796600+picnixz@users.noreply.github.com>
# - Hugo van Kemenade <1324225+hugovk@users.noreply.github.com>
# - Victor Stinner <vstinner@python.org>
# - Éric <merwok@netwok.org>
# - Grigory Bukovsky <booqoofsky@yandex.ru>
# 
# References:
# - RFC 9562: https://www.rfc-editor.org/rfc/rfc9562.html#section-5.7
# - Python `uuid` module: https://github.com/python/cpython/blob/main/Lib/uuid.py
# 
# Copyright (c) Python Software Foundation. All rights reserved.
# This code is licensed under the Python Software Foundation License.
"""
Typical usage:

    >>> import uuid7 as uuid

    # make a random UUID
    >>> uuid.uuid7()    # doctest: +SKIP
    UUID('00976400-be40-7de7-a772-38c88bd11b81')
"""
from os import urandom
from time import time_ns
# Importing all components from the `uuid` module to allow seamless usage of
# its functionalities alongside the UUIDv7 implementation provided in this module.
from uuid import *

# Define the new properties and methods for the UUID class.

def _hex(self: UUID) -> str:
    return self.bytes.hex()

def _str(self: UUID) -> str:
    x = self.hex
    return f'{x[:8]}-{x[8:12]}-{x[12:16]}-{x[16:20]}-{x[20:]}'

def _time(self: UUID) -> int:
    if self.version == 7:
        # unix_ts_ms (48) | ... (80)
        return self.int >> 80
    else:
        # time_lo (32) | time_mid (16) | ver (4) | time_hi (12) | ... (64)
        #
        # For compatibility purposes, we do not warn or raise when the
        # version is not 1 (timestamp is irrelevant to other versions).
        time_hi = (self.int >> 64) & 0x0fff
        time_lo = self.int >> 96
        return time_hi << 48 | (self.time_mid << 32) | time_lo

# Then monkey-patching the UUID class to add the new properties and methods.
UUID.hex = property(_hex)
UUID.time = property(_time)
UUID.__str__ = _str

##################################################
# UUIDv7 implementation sourced from Python 3.14 #
##################################################

_UINT_128_MAX = (1 << 128) - 1
_RFC_4122_VERSION_7_FLAGS = ((7 << 76) | (0x8000 << 48))

_last_timestamp_v7 = None
_last_counter_v7 = 0  # 42-bit counter

def _uuid7_get_counter_and_tail():
    rand = int.from_bytes(urandom(10))
    # 42-bit counter with MSB set to 0
    counter = (rand >> 32) & 0x1ff_ffff_ffff
    # 32-bit random data
    tail = rand & 0xffff_ffff
    return counter, tail

def uuid7():
    """
    Generate a UUID from a Unix timestamp in milliseconds and random bits.

    UUIDv7 objects feature monotonicity within a millisecond.
    """
    # --- 48 ---   -- 4 --   --- 12 ---   -- 2 --   --- 30 ---   - 32 -
    # unix_ts_ms | version | counter_hi | variant | counter_lo | random
    #
    # 'counter = counter_hi | counter_lo' is a 42-bit counter constructed
    # with Method 1 of RFC 9562, §6.2, and its MSB is set to 0.
    #
    # 'random' is a 32-bit random value regenerated for every new UUID.
    #
    # If multiple UUIDs are generated within the same millisecond, the LSB
    # of 'counter' is incremented by 1. When overflowing, the timestamp is
    # advanced and the counter is reset to a random 42-bit integer with MSB
    # set to 0.

    global _last_timestamp_v7
    global _last_counter_v7

    nanoseconds = time_ns()
    timestamp_ms = nanoseconds // 1_000_000

    if _last_timestamp_v7 is None or timestamp_ms > _last_timestamp_v7:
        counter, tail = _uuid7_get_counter_and_tail()
    else:
        if timestamp_ms < _last_timestamp_v7:
            timestamp_ms = _last_timestamp_v7 + 1
        # advance the 42-bit counter
        counter = _last_counter_v7 + 1
        if counter > 0x3ff_ffff_ffff:
            # advance the 48-bit timestamp
            timestamp_ms += 1
            counter, tail = _uuid7_get_counter_and_tail()
        else:
            # 32-bit random data
            tail = int.from_bytes(urandom(4))

    unix_ts_ms = timestamp_ms & 0xffff_ffff_ffff
    counter_msbs = counter >> 30
    # keep 12 counter's MSBs and clear variant bits
    counter_hi = counter_msbs & 0x0fff
    # keep 30 counter's LSBs and clear version bits
    counter_lo = counter & 0x3fff_ffff
    # ensure that the tail is always a 32-bit integer (by construction,
    # it is already the case, but future interfaces may allow the user
    # to specify the random tail)
    tail &= 0xffff_ffff

    int_uuid_7 = unix_ts_ms << 80
    int_uuid_7 |= counter_hi << 64
    int_uuid_7 |= counter_lo << 32
    int_uuid_7 |= tail
    # by construction, the variant and version bits are already cleared
    int_uuid_7 |= _RFC_4122_VERSION_7_FLAGS

    # UUID._from_int(value)
    assert 0 <= int_uuid_7 <= _UINT_128_MAX, repr(int_uuid_7)
    res = object.__new__(UUID)
    object.__setattr__(res, 'int', int_uuid_7)
    object.__setattr__(res, 'is_safe', SafeUUID.unknown)

    # defer global update until all computations are done
    _last_timestamp_v7 = timestamp_ms
    _last_counter_v7 = counter
    return res