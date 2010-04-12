#!/usr/bin/python
"""
Design by Contract in Python.

@description: This project enables to use the basics of Design by Contract capabilities in Python,
              such as enforcing the contracts defined in the epydoc documentation.

@copyright: Alex Myodov <amyodov@gmail.com>

@url: http://code.google.com/p/python-dbc/
"""

from itertools import izip, chain
import inspect


def typed(var, types):
    """
    Ensure that the "var" argument is among the types passed as the "types" argument.

    @param var: The argument to be typed.

    @param types: A tuple of types to check.
    @type types: tuple

    @returns: The var argument.

    >>> a = typed("abc", str)
    >>> type(a)
    <type 'str'>

    >>> b = typed("abc", int) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    AssertionError: Variable abc of type <type 'str'> not among the allowed types: <type 'int'>

    >>> c = typed(None, int) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    AssertionError: Variable None of type <type 'NoneType'> not among the allowed types: <type 'int'>
    """
    assert isinstance(var, types), \
        "Variable %s of type %s not among the allowed types: %s" % (var, type(var), repr(types))
    return var


def ntyped(var, types):
    """
    Ensure that the "var" argument is among the types passed as the "types" argument, or is None.

    @param var: The argument to be typed.

    @param types: A tuple of types to check.
    @type types: tuple

    @returns: The var argument.

    >>> a = ntyped("abc", str)
    >>> type(a)
    <type 'str'>

    >>> b = ntyped("abc", int) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    AssertionError: Variable abc of type <type 'str'> not among the allowed types: NoneType, <type 'int'>

    >>> c = ntyped(None, int) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    """
    assert var is None or isinstance(var, types), \
        "Variable %s of type %s not among the allowed types: NoneType, %s" % (var, type(var), repr(types))
    return var


def consists_of(seq, types):
    """
    Check that the all elements from the "seq" argument (sequence) are among the types passed as the "types" argument.

    @param seq: The sequence which elements are to be typed.

    @param types: A tuple of types to check.
    @type types: tuple

    @return: Whether the check succeeded.
    @rtype: bool

    >>> consists_of([5, 6, 7], int)
    True
    >>> consists_of([5, 6, 7, "abc"], int)
    False
    >>> consists_of([5, 6, 7, "abc"], (int, str))
    True
    """
    return all(isinstance(element, types) for element in seq)


def epydoc_contract(f):
    """
    The decorator for any functions which have a epydoc-formatted docstring.
    It validates the function inputs and output against the contract defined by the epydoc description.

    Currently, it supports the usual functions as well as simple object methods
    (though neither classmethods nor staticmethods).

    Inside the epydoc contracts, it supports the following fields:

    - C{@type arg:} - the type of the C{arg} argument is validated before the function is called.

    - C{@rtype:} - the return type of the function is validated after the function is called.

    - C{@precondition:} - the precondition (that may involve the arguments of the function)
        that should be satisfied before the function is executed.

    - C{@postcondition:} - the postcondition (that may involve the result of the function given as C{result} variable)
        that should be satisfied after the function is executed.

    @param f: The function which epydoc documentation should be verified.
    @precondition: callable(f)
    """
    if __debug__:
        try:
            from epydoc import apidoc, docbuilder, markup
        except ImportError:
            raise ImportError("To use epydoc_contract() function, "
                              "you must have the epydoc module (often called python-epydoc) installed.\n"
                              "For more details about epydoc installation, see http://epydoc.sourceforge.net/")

        module = inspect.getmodule(f)
        base_function_list = [i[3] for i in inspect.stack()]
        if "<module>" in base_function_list:
            base_function_list = base_function_list[:base_function_list.index("<module>")]

        base_function_path = list(reversed(base_function_list))[:-1]

        if not hasattr(module, "_dbc_ds_linker"):
            module._dbc_ds_linker = markup.DocstringLinker()

        contract = docbuilder.build_doc(f)

        preconditions = [description.to_plaintext(module._dbc_ds_linker)
                             for field, argument, description in contract.metadata
                             if field.singular == "Precondition"]
        postconditions = [description.to_plaintext(module._dbc_ds_linker)
                              for field, argument, description in contract.metadata
                              if field.singular == "Postcondition"]

        if isinstance(f, (staticmethod, classmethod)):
            raise NotImplementedError("Unfortunately, the @epydoc_contract decorator is not supported "
                                      "for either staticmethod or classmethod functions.")
        elif isinstance(contract, apidoc.RoutineDoc):
            dm = contract.defining_module
            f_location = "%s module (%s), %s()" % (contract.defining_module.canonical_name,
                                                   contract.defining_module.filename,
                                                   ".".join(base_function_path + [f.__name__]))
        else:
            raise Exception("@epydoc_contract decorator is not yet supported for %s types!" % type(contract))


        # ---

        def parse_str_to_value(value_str, entity_name, _globals = None, _locals = None):
            if _globals is None:
                _globals = globals()
            if _locals is None:
                _locals = locals()

            try:
                expected_value = eval(value_str, _globals, _locals)
            except Exception, e:
                raise SyntaxError("%s: "
                                  "the following %s "
                                  "could not be parsed: %s\n" % (f_location,
                                                                 entity_name,
                                                                 value_str))
            return expected_value

        # ---

        def parse_str_to_type(type_str, entity_name, _globals = None, _locals = None):
            expected_type = parse_str_to_value(type_str,
                                               "type definition for %s" % entity_name,
                                               _globals,
                                               _locals)

            if not isinstance(expected_type, (type, tuple)):
                raise SyntaxError("%s: "
                                  "the following type definition for %s "
                                  "should define a type rather than a %s entity: "
                                  "%s" % (f_location,
                                          entity_name,
                                          type(expected_type),
                                          type_str))

            return expected_type

        # ---

        def wrapped_f(*args, **kwargs):
            # For "globals" dictionary, we should use the globals of the code
            # that called the wrapper function.
            _globals = inspect.getargvalues(inspect.stack()[1][0])[3]

            arguments_to_validate = list(contract.arg_types)

            expected_types = dict((argument, parse_str_to_type(contract.arg_types[argument].to_plaintext(module._dbc_ds_linker),
                                                               "%s argument" % argument,
                                                               _globals = _globals))
                                      for argument in arguments_to_validate)


            # All values
            values = dict(chain(izip(contract.posargs, args),
                                kwargs.iteritems()))

            # Validate arguments
            for argument in arguments_to_validate:
                value = values[argument]
                expected_type = expected_types[argument]

                if not isinstance(value, expected_type):
                    raise TypeError("%s: "
                                    "The %s argument is of %s while must be of %s; "
                                    "its value is %s" % (f_location,
                                                         argument,
                                                         type(value),
                                                         expected_type,
                                                         repr(value)))

            # Validate preconditions
            locals_for_preconditions = dict(_globals)
            locals_for_preconditions.update(values)
            for description_str in preconditions:
                value = parse_str_to_value(description_str,
                                           "precondition definition",
                                           _globals = _globals,
                                           _locals = locals_for_preconditions)
                if not value:
                    raise ValueError("%s: "
                                     "The following precondition results in logical False; "
                                     "its definition is:\n"
                                     "\t%s\n"
                                     "and its real value is %s" % (f_location,
                                                                   description_str.strip(),
                                                                   repr(value)))

            #
            # Call the desired function
            #
            result = f(*args, **kwargs)

            # Validate return value
            if contract.return_type is not None:

                expected_type = parse_str_to_type(contract.return_type.to_plaintext(module._dbc_ds_linker),
                                                  "return value",
                                                  _globals = _globals)

                if not isinstance(result, expected_type):
                    raise TypeError("%s: " \
                                    "The following return value is of %s while must be of %s: "
                                    "%s" % (f_location,
                                            type(result),
                                            expected_type,
                                            repr(result)))

            # Validate postconditions
            locals_for_postconditions = dict(_globals)
            locals_for_postconditions.update({"result": result})
            for description_str in postconditions:
                value = parse_str_to_value(description_str,
                                           "postcondition definition",
                                           _locals = locals_for_postconditions)
                if not value:
                    raise ValueError("%s: "
                                     "The following postcondition results in logical False; "
                                     "its definition is:\n"
                                     "\t%s\n"
                                     "and its real value is %s" % (f_location,
                                                                   description_str.strip(),
                                                                   repr(value)))

            # Validations are successful
            return result

        # ---


        # Fix the parameters of the function
        wrapped_f.func_name = f.func_name
        return wrapped_f
    else:
        return f



if __debug__:

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
        TypeError: ... module (...), f(): The a1 argument is of <type 'int'> \
                   while must be of <type 'str'>; its value is 1
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
        TypeError: ... module (...), f(): The following return value is of <type 'str'> \
                   while must be of <type 'int'>:
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
        ValueError: ... module (...), f(): The following precondition results in logical False; \
                    its definition is:
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
        ValueError: ... module (...), f(): The following postcondition results in logical False; \
                    its definition is:
            result > 0
        and its real value is False

        >>> # Test implicit boolean expression. 4 + 6 = 10, 10 % 2 = 0, bool(0) = False
        >>> r = f(4, 6) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
          ...
        ValueError: ... module (...), f(): The following postcondition results in logical False; \
                    its definition is:
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
        TypeError: ... module (...), A.B.f(): The a1 argument is of <type 'int'> \
                   while must be of <type 'str'>; its value is 1
        """


if __name__ == "__main__":
    import doctest
    doctest.testmod()
