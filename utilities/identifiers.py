import importlib


def resolve_attr(obj, path):
    """A recursive version of getattr for navigating dotted paths.

    Args:
        obj: An object for which we want to retrieve a nested attribute.
        path: A dot separated string containing zero or more attribute names.

    Returns:
        The attribute referred to by obj.a1.a2.a3...

    Raises:
        AttributeError: If there is no such attribute.
    """
    if not path:
        return obj
    head, _, tail = path.partition('.')
    head_obj = getattr(obj, head)
    return resolve_attr(head_obj, tail)


MODULE_CLASS_SEPARATOR = '#'


def class_to_qualname(cls):
    """Obtain the qualified name of a class object.

    Args:
        cls: A class object.

    Returns:
        The returned string is of the form 'module.submodule#class.nested_class'
        with the dot-separated identifiers to the left of the hash symbol being
        module names, and the dot-separated identifiers to the right of the hash
        symbol being class names.

    """
    return cls.__module__ + MODULE_CLASS_SEPARATOR + cls.__qualname__


def qualname_to_class(qualname):
    """Obtain a class object by resolving a qualified name.

    Args:
        qualname: A fully qualified class name of the form
        'module.submodule#class.nested_class' with the dot-separated identifiers
        to the left of the hash symbol being module names, and the dot-separated
        identifiers to the right of the hash symbol being class names.

    Returns:
        A class object.

    Raises:
        AttributeError: If the qualname could not be resolved to a class object.
    """
    module_name, _, class_name = qualname.partition(MODULE_CLASS_SEPARATOR)
    module = importlib.import_module(module_name)
    cls = resolve_attr(module, class_name)
    return cls
