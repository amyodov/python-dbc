#!/usr/bin/python
"""
Design by Contract in Python - test module.

@description: This module executes various tests for the Design by Contract functionality in python-dbc module.

@copyright: Alex Myodov <amyodov@gmail.com>

@url: http://code.google.com/p/python-dbc/
"""
from dbc import contract_epydoc
#import test

#@contract_epydoc
def f2(a1):
    """
    @type a1: str
    """
    return a1


class A(object):
    class B:
        @staticmethod
        @contract_epydoc
        def m1(a2):
            """
            @type a2: (int, long)
            """
            return a2 + 5


def test_type():
    """
    >> r = f2(1) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    TypeError: test.type module (...), f2():
    The 'a1' argument is of <type 'int'> while must be of <type 'str'>; its value is 1

    >>> A.B.m1(17)
    22
    """


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    #test.test()
