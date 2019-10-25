# -*- coding: utf-8 -*-

"""Json Box module."""

from __future__ import absolute_import

from multiprocessing import Array
from ctypes import c_char

class JsonBox:
    def __init__(self):
        self._buffer = Array(c_char, 2500000)
        self._json = Array(c_char, 1024)

    def add(self, data):
        self._buffer.value += data

    def has_json(self):
        end = self._buffer.value.find(b'}')

        if end >= 0:
            start = self._buffer.value.rfind(b'{', 0, end)

            if start >= 0:
                self._json.value = self._buffer.value[start:end+1]
                self._buffer.value = self._buffer.value[end+1:]

                return True
            else:
                self._buffer.value = self._buffer.value[end+1:]

                return False
        else:
            start = self._buffer.value.rfind(b'{')

            if start >= 0:
                self._buffer.value = self._buffer.value[start:]
            else:
                self._buffer.value = b''

            return False

    @property
    def json(self):
        return self._json.value
