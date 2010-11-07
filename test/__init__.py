#!/usr/bin/env python
import doctest

modules = ("_01_simple_functions",
           "_02_class",
          )

for m in modules:
    exec("%(name)s = __import__('%(name)s', globals(), locals())" % {"name": m})


def test():
    gl = globals()
    for m in modules:
        doctest.testmod(gl[m])


if __name__ == "__main__":
    test()
