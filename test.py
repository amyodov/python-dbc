#!/usr/bin/python
"""
Design by Contract in Python - test module.

@description: This module executes various tests for the Design by Contract functionality in python-dbc module.

@copyright: Alex Myodov <amyodov@gmail.com>

@url: http://code.google.com/p/python-dbc/
"""

import dbc
from dbc import epydoc_contract


def test_type():
    """
    >>> @epydoc_contract
    ... def f(a1):
    ...     '''
    ...     @type a1: str
    ...     '''
    ...     return a1 + 1
    >>> r = f(1) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    TypeError: ... module (...), f():
    The 'a1' argument is of <type 'int'> while must be of <type 'str'>; its value is 1
    """

def test_rtype():
    """
    >>> @epydoc_contract
    ... def f(a1):
    ...     '''
    ...     @rtype: int
    ...     '''
    ...     return a1
    >>> r = f("a") # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    TypeError: ... module (...), f():
    The following return value is of <type 'str'> while must be of <type 'int'>:
        'a'
    """

def test_precondition():
    """
    >>> @epydoc_contract
    ... def f(a1, a2):
    ...     '''
    ...     @precondition: a1 > 0
    ...     @precondition: a2 > 0
    ...     @precondition: a1 + a2 > 0
    ...     '''
    ...     return a1 + a2
    >>> r = f(5, 6) # Nothing wrong
    >>> r = f(-5, 0) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    ValueError: ... module (...), f():
    The following precondition results in logical False; its definition is:
        a1 > 0
    and its real value is False
    """

def test_postcondition():
    """
    >>> @epydoc_contract
    ... def f(a1, a2):
    ...     '''
    ...     @postcondition: result > 0
    ...     @postcondition: result % 2
    ...     '''
    ...     return a1 + a2

    >>> r = f(3, 6) # Nothing wrong

    >>> # Test explicit boolean expression
    >>> r = f(-6, 3) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    ValueError: ... module (...), f():
    The following postcondition results in logical False; its definition is:
        result > 0
    and its real value is False

    >>> # Test implicit boolean expression. 4 + 6 = 10, 10 % 2 = 0, bool(0) = False
    >>> r = f(4, 6) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    ValueError: ... module (...), f():
    The following postcondition results in logical False; its definition is:
        result % 2
    and its real value is 0
    """

def test_class():
    """
    >>> class A(object):
    ...     class B(object):
    ...         @staticmethod
    ...         @epydoc_contract
    ...         def f(a1):
    ...             '''
    ...             @type a1: str
    ...             '''
    ...             return a1

    >>> r = A.B.f("")

    >>> r = A.B.f(1) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    TypeError: ... module (...), A.B.f():
    The 'a1' argument is of <type 'int'> while must be of <type 'str'>; its value is 1
    """


class MyNum(object):

    @epydoc_contract
    def __init__(self, i):
        """
        @type i: (int, long)
        """
        self.i = i


    @epydoc_contract
    def __repr__(self):
        """
        @type self: MyNum
        @rtype: basestring
        @postcondition: 'MyNum' in result
        """
        return "<MyNum %i>" % self.i


    @staticmethod
    @epydoc_contract
    def from_string(in_str):
        """
        @type in_str: basestring
        @rtype: MyNum
        """
        return MyNum(int(in_str))


    @classmethod
    @epydoc_contract
    def from_string_cls(cls, in_str):
        """
        @precondition: issubclass(cls, MyNum)
        @type in_str: basestring
        @rtype: MyNum
        """
        return MyNum(int(in_str))


    @epydoc_contract
    def __add__(self, other):
        """
        @precondition: isinstance(other, MyNum)
        @type other: MyNum

        @rtype: MyNum
        @postcondition: result.i == self.i + other.i
        @postcondition: type(result) == MyNum
        """
        return MyNum(self.i + other.i)


def test_mynum_class():
    """
    >>> a = MyNum(15); a
    <MyNum 15>

    >>> b = MyNum.from_string('16'); b
    <MyNum 16>

    >>> a + b
    <MyNum 31>

    >>> c = MyNum.from_string_cls('17'); c
    <MyNum 17>
    """


if __name__ == "__main__":
#    import doctest
#    doctest.testmod(__init__)
#    doctest.testmod()

    a = MyNum(15)
    #b = MyNum.from_string('16')
    #print a + b
    #c = MyNum.from_string_cls('17')
