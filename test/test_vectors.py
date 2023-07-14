# file: test_vectors.py
# vim:fileencoding=utf-8:fdm=marker:ft=python
#
# Copyright © 2023 R.F. Smith <rsmith@xs4all.nl>
# SPDX-License-Identifier: MIT
# Created: 2023-07-14T17:20:01+0200
# Last modified: 2023-07-14T17:39:02+0200
"""
Test the vector manipulation functions.

This code is meant to be used by py.test from the root directory of the project.
"""

import random
import sys
import math

# Inserting the path is needed to make sure that the module here is loaded,
# not an installed version!
sys.path.insert(1, ".")

ao = __import__("auto-orient")


def len(v):
    return math.sqrt(sum(num * num for num in v))


def test_normalize():
    a = (random.randint(1, 100), random.randint(1, 100), random.randint(1, 100))
    an = ao.normalize(a)
    assert math.isclose(len(an), 1)


def test_isclose():
    a = (1, 0, 0)
    b = ao.normalize((1, 0, 0.001))
    assert ao.isclose(a, b)


def test_cross():
    a = (1, 0, 0)
    b = (0, 1, 0)
    assert ao.cross(a, b) == (0, 0, 1)


def test_dot():
    assert ao.dot((1, 0, 0), (0, 1, 0)) == 0
    a = (random.randint(1, 100), random.randint(1, 100), random.randint(1, 100))
    assert ao.dot(a, a) == 1
