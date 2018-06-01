#
# Copyright (C) 2012 - 2018 Satoru SATOH <ssato @ redhat.com>
# License: MIT
#
"""Misc utility routines for anyconfig module.
"""
from __future__ import absolute_import

import collections
import glob
import os.path
import types

import anyconfig.compat
import anyconfig.globals

from anyconfig.compat import pathlib


def get_file_extension(file_path):
    """
    >>> get_file_extension("/a/b/c")
    ''
    >>> get_file_extension("/a/b.txt")
    'txt'
    >>> get_file_extension("/a/b/c.tar.xz")
    'xz'
    """
    _ext = os.path.splitext(file_path)[-1]
    if _ext:
        return _ext[1:] if _ext.startswith('.') else _ext

    return ""


def sglob(files_pattern):
    """
    glob.glob alternative of which results sorted always.
    """
    return sorted(glob.glob(files_pattern))


def is_iterable(obj):
    """
    >>> is_iterable([])
    True
    >>> is_iterable(())
    True
    >>> is_iterable([x for x in range(10)])
    True
    >>> is_iterable((1, 2, 3))
    True
    >>> g = (x for x in range(10))
    >>> is_iterable(g)
    True
    >>> is_iterable("abc")
    False
    >>> is_iterable(0)
    False
    >>> is_iterable({})
    False
    """
    return isinstance(obj, (list, tuple, types.GeneratorType)) or \
        (not isinstance(obj, (int, str, dict)) and
         bool(getattr(obj, "next", False)))


def concat(xss):
    """
    Concatenates a list of lists.

    >>> concat([[]])
    []
    >>> concat((()))
    []
    >>> concat([[1,2,3],[4,5]])
    [1, 2, 3, 4, 5]
    >>> concat([[1,2,3],[4,5,[6,7]]])
    [1, 2, 3, 4, 5, [6, 7]]
    >>> concat(((1,2,3),(4,5,[6,7])))
    [1, 2, 3, 4, 5, [6, 7]]
    >>> concat(((1,2,3),(4,5,[6,7])))
    [1, 2, 3, 4, 5, [6, 7]]
    >>> concat((i, i*2) for i in range(3))
    [0, 0, 1, 2, 2, 4]
    """
    return list(anyconfig.compat.from_iterable(xs for xs in xss))


def normpath(path):
    """Normalize path.

    - eliminating double slashes, etc. (os.path.normpath)
    - ensure paths contain ~[user]/ expanded.

    :param path: Path string :: str
    """
    return os.path.normpath(os.path.expanduser(path) if '~' in path else path)


def is_path(obj):
    """
    Is given object `obj` a file path?

    :param obj: file path or something
    :return: True if `obj` is a file path
    """
    return isinstance(obj, anyconfig.compat.STR_TYPES)


def is_path_obj(obj):
    """Is given object `input` a pathlib.Path object?

    :param obj: Input object may be pathlib.Path object or something
    :return: True if `obj` is a pathlib.Path object

    >>> from anyconfig.compat import pathlib
    >>> if pathlib is not None:
    ...      obj = pathlib.Path(__file__)
    ...      assert is_path_obj(obj)
    >>>
    >>> assert not is_path_obj(__file__)
    """
    return pathlib is not None and isinstance(obj, pathlib.Path)


def is_file_stream(obj):
    """Is given object `input` a file stream (file/file-like object)?

    :param obj: Input object may be pathlib.Path object or something
    :return: True if `obj` is a file stream

    >>> assert is_file_stream(open(__file__))
    >>> assert not is_file_stream(__file__)
    """
    return getattr(obj, "read", False)


def is_io_obj(obj, keys=None):
    """
    :return: True if given `obj` is a 'Input' or 'Output' namedtuple object.

    >>> assert not is_io_obj(1)
    >>> assert not is_io_obj("aaa")
    >>> assert not is_io_obj({})
    >>> assert not is_io_obj(('a', 1, {}))

    >>> inp = anyconfig.globals.Input("/etc/hosts", "path", "/etc/hosts",
    ...                               None, open)
    >>> assert is_io_obj(inp)
    """
    if keys is None:
        return is_io_obj(obj, anyconfig.globals.INPUT_KEYS) or \
               is_io_obj(obj, anyconfig.globals.OUTPUT_KEYS)

    if isinstance(obj, tuple) and getattr(obj, "_asdict", False):
        return all(k in obj._asdict() for k in keys)

    return False


def is_path_like_object(obj, marker='*'):
    """
    Is given object `obj` a path string or a pathlib.Path object or a file
    stream (file/file-like object) or Input/Output namedtuple?

    :param obj:
        An object may be a path string, pathlib.Path object, a file stream or
        an Input/Output namedtuple

    :return:
        True if `obj` is a path string or a pathlib.Path object or a file
        (stream) object

    >>> assert is_path_like_object(__file__)
    >>> assert not is_path_like_object("/a/b/c/*.json", '*')

    >>> from anyconfig.compat import pathlib
    >>> if pathlib is not None:
    ...      assert is_path_like_object(pathlib.Path("a.ini"))
    ...      assert not is_path_like_object(pathlib.Path("x.ini"), 'x')

    >>> assert is_path_like_object(open(__file__))
    """
    return ((is_path(obj) and marker not in obj) or
            (is_path_obj(obj) and marker not in obj.as_posix()) or
            is_file_stream(obj) or is_io_obj(obj))


def is_paths(maybe_paths, marker='*'):
    """
    Does given object `maybe_paths` consist of path or path pattern strings?
    """
    return ((is_path(maybe_paths) and marker in maybe_paths) or  # Path str
            (is_path_obj(maybe_paths) and marker in maybe_paths.as_posix()) or
            (is_iterable(maybe_paths) and
             all(is_path(p) or is_io_obj(p) for p in maybe_paths)))


def is_input_obj(obj):
    """
    :return: True if given something `obj` is a 'Input' namedtuple object.

    >>> obj = anyconfig.globals.Input("/etc/hosts", "path", "/etc/hosts",
    ...                               None, open)
    >>> assert is_input_obj(obj)
    """
    return is_io_obj(obj, keys=anyconfig.globals.INPUT_KEYS)


def is_output_obj(obj):
    """
    :return: True if given something `obj` is a 'Output' namedtuple object.

    >>> obj = anyconfig.globals.Output("/etc/hosts", "path", "/etc/hosts",
    ...                                None, open)
    >>> assert is_output_obj(obj)
    """
    return is_io_obj(obj, keys=anyconfig.globals.OUTPUT_KEYS)


def get_path_from_stream(strm):
    """
    Try to get file path from given file or file-like object `strm`.

    :param strm: A file or file-like object
    :return: Path of given file or file-like object or None
    :raises: ValueError

    >>> assert __file__ == get_path_from_stream(open(__file__, 'r'))
    >>> assert get_path_from_stream(anyconfig.compat.StringIO()) is None
    >>> get_path_from_stream(__file__)  # doctest: +ELLIPSIS
    Traceback (most recent call last):
        ...
    ValueError: ...
    """
    if not is_file_stream(strm):
        raise ValueError("Given object does not look a file/file-like "
                         "object: %r" % strm)

    path = getattr(strm, "name", None)
    if path is not None:
        return normpath(path)

    return None


def _try_to_get_extension(obj):
    """
    Try to get file extension from given path or file object.

    :param obj: a file, file-like object or something
    :return: File extension or None

    >>> _try_to_get_extension("a.py")
    'py'
    """
    if is_path(obj):
        path = obj

    elif is_path_obj(obj):
        return obj.suffix[1:]

    elif is_file_stream(obj):
        try:
            path = get_path_from_stream(obj)
        except ValueError:
            return None

    elif is_io_obj(obj):
        path = obj.path

    else:
        return None

    return path and get_file_extension(path) or None


def are_same_file_types(paths):
    """
    Are given (maybe) file paths same type (extension) ?

    :param paths: A list of file path or file(-like) objects

    >>> are_same_file_types([])
    False
    >>> are_same_file_types(["a.conf"])
    True
    >>> are_same_file_types(["a.conf", "b.conf"])
    True
    >>> are_same_file_types(["a.yml", "b.yml"])
    True
    >>> are_same_file_types(["a.yml", "b.json"])
    False
    >>> strm = anyconfig.compat.StringIO()
    >>> are_same_file_types(["a.yml", "b.yml", strm])
    False
    """
    if not paths:
        return False

    ext = _try_to_get_extension(paths[0])
    if ext is None:
        return False

    return all(_try_to_get_extension(p) == ext for p in paths[1:])


def _norm_paths_itr(inputs, marker='*'):
    """Iterator version of :func:`norm_inputs`.
    """
    for inp in inputs:
        if is_path(inp):
            if marker in inp:  # glob path pattern
                for ppath in sglob(inp):
                    yield ppath
            else:
                yield inp  # a simple file path
        elif is_path_obj(inp):
            if marker in inp.as_posix():
                for ppath in sglob(inp.as_posix()):
                    yield normpath(ppath)
            else:
                yield normpath(inp.as_posix())
        elif is_io_obj(inp):
            yield inp.path
        else:  # A file or file-like object
            yield inp


def norm_paths(paths, marker='*'):
    """
    :param paths:
        A glob path pattern string or pathlib.Path object holding such path, or
        a list consists of path strings or glob path pattern strings or
        pathlib.Path object holding such ones, or file objects
    :param marker: Glob marker character or string, e.g. '*'

    :return: List of path strings

    >>> norm_paths([])
    []
    >>> norm_paths("/usr/lib/a/b.conf /etc/a/b.conf /run/a/b.conf".split())
    ['/usr/lib/a/b.conf', '/etc/a/b.conf', '/run/a/b.conf']
    >>> paths_s = os.path.join(os.path.dirname(__file__), "u*.py")
    >>> ref = sglob(paths_s)
    >>> assert norm_paths(paths_s) == ref
    >>> ref = ["/etc/a.conf"] + ref
    >>> assert norm_paths(["/etc/a.conf", paths_s]) == ref
    >>> strm = anyconfig.compat.StringIO()
    >>> assert norm_paths(["/etc/a.conf", strm]) == ["/etc/a.conf", strm]
    """
    if is_path(paths) and marker in paths:
        return sglob(paths)

    if is_path_obj(paths) and marker in paths.as_posix():
        # TBD: Is it better to return [p :: pathlib.Path] instead?
        return [normpath(p) for p in sglob(paths.as_posix())]

    return list(_norm_paths_itr(paths, marker=marker))


# pylint: disable=unused-argument
def noop(val, *args, **kwargs):
    """A function does nothing.

    >>> noop(1)
    1
    """
    # It means nothing but can suppress 'Unused argument' pylint warns.
    # (val, args, kwargs)[0]
    return val


_LIST_LIKE_TYPES = (collections.Iterable, collections.Sequence)


def is_dict_like(obj):
    """
    :param obj: Any object behaves like a dict.

    >>> is_dict_like("a string")
    False
    >>> is_dict_like({})
    True
    >>> is_dict_like(anyconfig.compat.OrderedDict((('a', 1), ('b', 2))))
    True
    """
    return isinstance(obj, (dict, collections.Mapping))  # any others?


def is_namedtuple(obj):
    """
    >>> p0 = collections.namedtuple("Point", "x y")(1, 2)
    >>> is_namedtuple(p0)
    True
    >>> is_namedtuple(tuple(p0))
    False
    """
    return isinstance(obj, tuple) and hasattr(obj, "_asdict")


def is_list_like(obj):
    """
    >>> is_list_like([])
    True
    >>> is_list_like(())
    True
    >>> is_list_like([x for x in range(10)])
    True
    >>> is_list_like((1, 2, 3))
    True
    >>> g = (x for x in range(10))
    >>> is_list_like(g)
    True
    >>> is_list_like("abc")
    False
    >>> is_list_like(0)
    False
    >>> is_list_like({})
    False
    """
    return isinstance(obj, _LIST_LIKE_TYPES) and \
        not (isinstance(obj, anyconfig.compat.STR_TYPES) or is_dict_like(obj))


def filter_options(keys, options):
    """
    Filter `options` with given `keys`.

    :param keys: key names of optional keyword arguments
    :param options: optional keyword arguments to filter with `keys`

    >>> filter_options(("aaa", ), dict(aaa=1, bbb=2))
    {'aaa': 1}
    >>> filter_options(("aaa", ), dict(bbb=2))
    {}
    """
    return dict((k, options[k]) for k in keys if k in options)

# vim:sw=4:ts=4:et:
