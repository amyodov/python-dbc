# Summary

This project enables to use the basics of Design by Contract capabilities in Python, such as enforcing the contracts defined in the [epydoc](http://epydoc.sourceforge.net/) documentation. **Even though it is somewhere experimental, it has been used in production for quite a time and seems stable enough.**

# Requirements

For the most important functionality of this module, you must have epydoc installed. Please refer to [epydoc](http://epydoc.sourceforge.net/) site or your Unix/Linux distribution regarding the installation details.

Though, you may use the more general helper functions like `typed()`, `ntyped()` or `consists_of()` from the module without using epydoc, if you just need to perform some simple type assertions.

# Usage

Are you (by some chance) tired of declaring the same assertions twice, first in the epydoc declaration (for better documentation), then in the code, to ensure they are indeed satisfied? 

    def hypo(leg_a, leg_b): 
        """
        @precondition: leg_a > 0
        @precondition: leg_b > 0
        @type leg_a: (int, float)
        @type leg_b: (int, float)
        @rtype: float
        @postcondition: result > 0
        """
        assert leg_a > 0, repr(leg_a)
        assert leg_b > 0, repr(leg_b)
        assert isinstance(leg_a, (int, float)), repr(leg_a)
        assert isinstance(leg_b, (int, float)), repr(leg_b)
        result = math.sqrt(leg_a**2 + leg_b**2)
        assert isinstance(result, float), repr(result)
        assert result > 0, repr(result)
        return result

Don't waste the code anymore. Just do this instead:

    from dbc import contract_epydoc
    
    @contract_epydoc
    def hypo(leg_a, leg_b):
        """
        @precondition: leg_a > 0
        @precondition: leg_b > 0
        @type leg_a: (int, float)
        @type leg_b: (int, float)
        @rtype: float
        @postcondition: result > 0
        """
        return math.sqrt(leg_a**2 + leg_b**2)

And all the assumptions and assertions defined in the epydoc docstring for the function are automagically checked whenever the function is called!

Note that having to verify all the incomes and outcomes may significantly decrease the performance; therefore, these verifications (similarly to the only DbC-related Python builtin `assert()` function) are completely disabled if the code is executed with optimization, i.e. via `python -O` or `python -OO`. The only runtime overhead from this module in optimized mode is calling the decorator itself once during the very first code interpretation pass.

# Notes

Don't do this:

    @contract_epydoc 
    @staticmethod
    def some_method(...):
        ...

or
    @contract_epydoc
    @classmethod
    def some_method(...):
        ...

Classmethods and staticmethods are not the proper functions, but the objects of special kind, so the function arguments cannot be checked for them.

Do this instead:

    @staticmethod
    @contract_epydoc
    def some_method(...):
        ...

or 
    @classmethod
    @contract_epydoc
    def some_method(...):
        ...

# Disclaimer

This code was in the production for about an year, and proven to work well and stable enough. Though your success may vary.

Feel free to send me comments and pull requests.
