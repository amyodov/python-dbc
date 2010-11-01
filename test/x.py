#!/usr/bin/python
import inspect
from types import FloatType, NoneType

from dbc import contract_epydoc

type2 = float

class A(object):
    class B:
        type1 = int


        @staticmethod
        @contract_epydoc
        def m1(a1):
            """
            @type a1: (int, long, type1, type2, NoneType)

            @rtype: (int, str)
            """
            return a1 + 5
