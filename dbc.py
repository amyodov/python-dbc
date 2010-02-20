#!/usr/bin/python

from epydoc import apidoc, docstringparser, docbuilder, markup


def epydoc_contract(f):
    if __debug__:
        def wrapped_f(*args, **kwargs):
            #print "DOC", dir(f)

            ds_linker = markup.DocstringLinker()

            contract = docbuilder.build_doc(f)

            if isinstance(contract, apidoc.RoutineDoc):
                f_location = "%s module (%s), %s()" % (contract.defining_module.canonical_name,
                                                       contract.defining_module.filename,
                                                       f.__name__)
                
            #print "RoutineDoc", dir(contract)
            #for k in dir(contract):
            #    print "  >>", k, getattr(contract, k)


            # Validate positional arguments
            posargs_values = dict(zip(contract.posargs, args))
            #print `posargs_values`

            posarg_to_type = dict((name, eval(descr.to_plaintext(ds_linker)) ) for name, descr in contract.arg_types.iteritems())

            #print `posarg_to_type`
            for posarg in contract.posargs:
                #print "POSARG", posarg
                if posarg in posarg_to_type:
                    value = posargs_values[posarg]
                    expected_type = posarg_to_type[posarg]
                    #print "Check", value, expected_type
                    if not isinstance(value, expected_type):
                        raise TypeError("%s: " \
                                        "The %s argument is %s of %s while must be of %s." % (f_location,
                                                                                              repr(posarg),
                                                                                              `value`,
                                                                                              type(value),
                                                                                              expected_type))

            result = f(*args)

            # Validate return value
            if contract.return_type is not None:
                rtype = type(result)
                expected_type = eval(contract.return_type.to_plaintext(ds_linker))
                #print "EXP", `expected_type`, `rtype`
                if not isinstance(result, expected_type):
                    raise TypeError("%s: " \
                                    "The return value is %s of %s while must be of %s." % (f_location,
                                                                                           repr(result),
                                                                                           type(result),
                                                                                           expected_type))

            # Validations are successful
            return result
        return wrapped_f
    else:
        return f

#def decoratorFunctionWithArguments(arg1, arg2, arg3):
#    def wrap(f):
#        print "Inside wrap()"
#        def wrapped_f(*args):
#            print "Inside wrapped_f()"
#            print "Decorator arguments:", arg1, arg2, arg3
#            f(*args)
#            print "After f(*args)"
#        return wrapped_f
#    return wrap



if __debug__:
    def test():
        """
        >>> @epydoc_contract
        ... def f1(a1):
        ...     '''
        ...     @type a1: str
        ...     '''
        ...     return a1 + 1
        >>> r = f1(1) # doctest:+ELLIPSIS
        Traceback (most recent call last):
           ...
        TypeError: __main__ module (...), f1(): The 'a1' argument is 1 of <type 'int'> while must be of <type 'str'>.

        >>> @epydoc_contract
        ... def f2(a1):
        ...     '''
        ...     @rtype: int
        ...     '''
        ...     return a1
        >>> r = f2("") # doctest:+ELLIPSIS
        Traceback (most recent call last):
           ...
        TypeError: __main__ module (...), f2(): The return value is '' of <type 'str'> while must be of <type 'int'>.
        """



if __name__ == "__main__":
    import doctest
    doctest.testmod()


@epydoc_contract
def f1(a1):
    """
    @rtype: int
    """
    return a1


r = f1(1)
