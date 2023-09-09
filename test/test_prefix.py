# file: test_prefix.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2023 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2023-09-09T10:09:01+0200
# Last modified: 2023-09-09T10:21:01+0200
"""Test that a list of 1000 generated prefixes does not contain repeats."""

import binascii
import random


def test_prefix_noseed():
    prefixes = [
        binascii.hexlify(random.randbytes(4)).decode("ascii").upper()
        for j in range(1001)
    ]
    origlen = len(prefixes)
    setlen = len(set(prefixes))
    assert origlen == setlen


def test_prefix_seeded():
    prefixes = []
    for j in range(1001):
        random.seed()
        prefixes.append(binascii.hexlify(random.randbytes(4)).decode("ascii").upper())
    origlen = len(prefixes)
    setlen = len(set(prefixes))
    assert origlen == setlen
