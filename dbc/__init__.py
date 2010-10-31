#!/usr/bin/env python
"""
Design by Contract in Python.

@description: This project enables to use the basics of Design by Contract capabilities in Python,
              such as enforcing the contracts defined in the epydoc documentation.

@copyright: Alex Myodov <amyodov@gmail.com>

@url: http://code.google.com/p/python-dbc/
"""

__all__ = ("typed", "ntyped", "consists_of", "contract_epydoc")

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
    AssertionError: Value 'abc' of type <type 'str'> is not among the allowed types: <type 'int'>

    >>> c = typed(None, int) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    AssertionError: Value None of type <type 'NoneType'> is not among the allowed types: <type 'int'>
    """
    assert isinstance(var, types), \
        "Value %r of type %r is not among the allowed types: %r" % (var, type(var), types)
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
    AssertionError: Value 'abc' of type <type 'str'> is not among the allowed types: NoneType, <type 'int'>

    >>> c = ntyped(None, int) # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    """
    assert var is None or isinstance(var, types), \
        "Value %r of type %r is not among the allowed types: NoneType, %r" % (var, type(var), types)
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


def _rpdb2():
    import rpdb2
    rpdb2.start_embedded_debugger("123")


def _get_function_base_path_from_stack(stack):
    """
    Given a stack (in the format as inspect.stack() returns),
    construct the path to the function (it may be a top-level in the module or defined in some deeper namespace,
    such as a class or another function).

    @param stack: The list similar in format to the result of inspect.stack().

    @return: The function fully qualified namespaces
             (with all intermediate namespaces where it is defined). The name of the function itself is not included.
    @rtype: basestring
    """
    base_function_list = [i[3] for i in reversed(stack)]
    # Start from a new module.
    if "<module>" in base_function_list:
        del base_function_list[:base_function_list.index("<module>") + 1]

    return ".".join(base_function_list)


def _parse_str_to_value(f_path, value_str, entity_name, _globals, _locals):
    """
    This function performs parsing
    """
    try:
        expected_value = eval(value_str, dict(_globals), dict(_locals))
    except Exception, e:
        import traceback; traceback.print_exc()
        raise SyntaxError("%s:\n"
                          "The following %s "
                          "could not be parsed: %s\n" % (f_path,
                                                         entity_name,
                                                         value_str))
    return expected_value

# ---

def _parse_str_to_type(f_path, type_str, entity_name, _globals = None, _locals = None):
    """
    @raises SyntaxError: If the string cannot be parsed as a valid type.
    """
    expected_type = _parse_str_to_value(f_path,
                                        type_str,
                                        "type definition for %s" % entity_name,
                                        _globals,
                                        _locals)

    if not isinstance(expected_type, (type, tuple)):
        raise SyntaxError("%s:\n"
                          "The following type definition for %s "
                          "should define a type rather than a %s entity: "
                          "%s" % (f_path,
                                  entity_name,
                                  type(expected_type),
                                  type_str))

    return expected_type



def contract_epydoc(f):
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
            raise ImportError("To use contract_epydoc() function, "
                              "you must have the epydoc module (often called python-epydoc) installed.\n"
                              "For more details about epydoc installation, see http://epydoc.sourceforge.net/")

        # Given a method/function, get the module where the function is defined.
        module = inspect.getmodule(f)
        _stack = inspect.stack()[1:]

        # The function/method marked with @contract_epydoc may be either top-level in the module,
        # or defined inside some namespace, like a class or another function.
        base_function_path = _get_function_base_path_from_stack(_stack)

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
            raise NotImplementedError("The @contract_epydoc decorator is not supported "
                                      "for either staticmethod or classmethod functions; "
                                      "please use it before (below) turning a function into "
                                      "a static method or a class method.")
        elif isinstance(contract, apidoc.RoutineDoc):
            dm = contract.defining_module
            f_path = "%(mod_name)s module (%(mod_file_path)s), %(func_name)s()" % {
                "mod_name"      : contract.defining_module.canonical_name,
                "mod_file_path" : contract.defining_module.filename,
                "func_name"     : "%s.%s" % (base_function_path, f.__name__)
                }
        else:
            raise Exception("@contract_epydoc decorator is not yet supported for %s types!" % type(contract))

        #
        # At this stage we have f_path

        # ---

        def wrapped_f(*args, **kwargs):
            _stack = inspect.stack()
            # For "globals" dictionary, we should use the globals of the code
            # that called the wrapper function.
            _globals = inspect.getargvalues(_stack[1][0])[3]

            #function_arguments = inspct.getargvalues(inspect.stack())
            l = 0
            for lev in _stack:
                r = inspect.getargvalues(lev[0])
                l += 1
            #lev = inspect.stack()[1]
            #
            #print "0:::", r[0]
            #if "self" in r[0] and "other" in r[0]:
            #    print "!!!!!!!!!!!!!!!!"
            #    print "!!!!!!!!!!!!!!!!"
            #    print "!!!!!!!!!!!!!!!!"
            #    print "!!!!!!!!!!!!!!!!"
            #    print "!!!!!!!!!!!!!!!!"
            #print "3:::", r[3].keys()
            #print ",,,,,,,,,,"

            #function_arguments = inspect.getargvalues(inspect.stack()[1][0])
            #print
            #print "GL0", f.__name__, `_globals.keys()`

            arguments_to_validate = list(contract.arg_types)

            expected_types = dict((argument, _parse_str_to_type(f_path,
                                                                contract.arg_types[argument].to_plaintext(module._dbc_ds_linker),
                                                                "'%s' argument" % argument,
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
                    raise TypeError("%s:\n"
                                    "The '%s' argument is of %r while must be of %r; "
                                    "its value is %r" % (f_path,
                                                         argument,
                                                         type(value),
                                                         expected_type,
                                                         value))

            # Validate preconditions
            locals_for_preconditions = values
            #print "GL1", f.__name__, `_globals.keys()`
            for description_str in preconditions:
                value = _parse_str_to_value(f_path,
                                            description_str,
                                            "precondition definition",
                                            _globals = _globals,
                                            _locals = locals_for_preconditions)
                if not value:
                    raise ValueError("%s:\n"
                                     "The following precondition results in logical False; "
                                     "its definition is:\n"
                                     "\t%s\n"
                                     "and its real value is %r" % (f_path,
                                                                   description_str.strip(),
                                                                   value))

            #
            # Call the desired function
            #
            glk0 = _globals.keys()
            result = f(*args, **kwargs)
            glk1 = _globals.keys()

            # Validate return value
            if contract.return_type is not None:

                expected_type = _parse_str_to_type(f_path,
                                                   contract.return_type.to_plaintext(module._dbc_ds_linker),
                                                   "return value",
                                                   _globals = _globals)

                if not isinstance(result, expected_type):
                    raise TypeError("%s:\n"
                                    "The following return value is of %r while must be of %r: "
                                    "%r" % (f_path,
                                            type(result),
                                            expected_type,
                                            result))

            # Validate postconditions
            locals_for_postconditions = {"result": result}
            for description_str in postconditions:
                value = _parse_str_to_value(f_path,
                                            description_str,
                                            "postcondition definition",
                                            _locals = locals_for_postconditions,
                                            _globals = _globals)
                if not value:
                    raise ValueError("%s:\n"
                                     "The following postcondition results in logical False; "
                                     "its definition is:\n"
                                     "\t%s\n"
                                     "and its real value is %r" % (f_path,
                                                                   description_str.strip(),
                                                                   value))

            # Validations are successful
            return result

        # ---


        # Fix the parameters of the function
        wrapped_f.func_name = f.func_name
        return wrapped_f
    else:
        return f
