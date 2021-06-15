#!/usr/bin/env python
"""
Free functions and helpers
"""



def str_toupper(text):
    return str(text).upper()



def get_function_ref(context, function_name:str) -> callable:
    """Helper that locates a class method (if it exists)

    Args:
        context (obj): The context of where we're going to search for the method.
            i.e., ``self`` if we're looking for a method within our class.
        function_name (str): The name of the class method we're searching for.

    Returns:
        callable: A reference to a callable method is returned if we are successful.
            Otherwise None

    Raises:
        AttributError: If the function is not found within the requested context.
        TypeError: If the attribute is found but is not callable.
    """

    function_ref = None

    function_ref = getattr(context, function_name)

    if not callable(function_ref):
        raise TypeError("{}.{} is not callable.".format(context, function_name))

    return function_ref






