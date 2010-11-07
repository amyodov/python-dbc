#!/usr/bin/python
"""
Design by Contract in Python - test module.

@description: This module executes various tests for the Design by Contract functionality in python-dbc module.

@copyright: Alex Myodov <amyodov@gmail.com>

@url: http://code.google.com/p/python-dbc/
"""
from dbc import contract_epydoc
import test
from types import LambdaType


@contract_epydoc
def f1(a1):
    """
    @type a1: str

    @precondition: len(a1) > 2

    @rtype: basestring
    @postcondition: len(result) == len(a1) + 3
    """
    if a1 == "bad output":
        return 17
    elif a1 == "bad postcondition":
        return "def"
    else:
        return "%sdef" % a1


def test_sanity_good():
    """
    >>> print f1('abcd') # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    abcddef
    """


def test_sanity_bad():
    """
    >>> r = f1(1) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    TypeError: __main__ module (...), f1():
    The 'a1' argument is of <type 'int'> while must be of <type 'str'>; its value is 1

    >>> r = f1('bad output') # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    TypeError: __main__ module (...), f1():
    The following return value is of <type 'int'> while must be of <type 'basestring'>: 17

    >>> r = f1('bad postcondition') # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    ValueError: __main__ module (...), f1():
    The following postcondition results in logical False; its definition is:
        len(result) == len(a1) + 3
    and its real value is False
    """

def test_sanity_remote_bad():
    """
    >> tuptup = tuple
    >> test._01_simple_functions.A.B.m1(17)
    22

    >>> mytype = test._02_class.MyType
    >>> a = mytype(42)
    >>> a
    <MyType: 42>

    >>> a + 15 # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    TypeError: test._02_class module (...), MyType.__add__():
    The 'other' argument is of <type 'int'> while must be of <class 'test._02_class.MyType'>; its value is 15
    """


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    test.test()
