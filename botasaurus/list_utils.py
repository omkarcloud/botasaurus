def iterflatten(array, depth=-1):
    """Iteratively flatten a list shallowly or deeply."""
    for item in array:
        if isinstance(item, (list, tuple)) and depth != 0:
            for subitem in iterflatten(item, depth - 1):
                yield subitem
        else:
            yield item

def flatten_depth(array, depth=1):
    """
    Recursively flatten `array` up to `depth` times.

    Args:
        array (list): List to flatten.
        depth (int, optional): Depth to flatten to. Defaults to ``1``.

    Returns:
        list: Flattened list.

    Example:

        >>> flatten_depth([[[1], [2, [3]], [[4]]]], 1)
        [[1], [2, [3]], [[4]]]
        >>> flatten_depth([[[1], [2, [3]], [[4]]]], 2)
        [1, 2, [3], [4]]
        >>> flatten_depth([[[1], [2, [3]], [[4]]]], 3)
        [1, 2, 3, 4]
        >>> flatten_depth([[[1], [2, [3]], [[4]]]], 4)
        [1, 2, 3, 4]

    .. versionadded:: 4.0.0
    """
    return list(iterflatten(array, depth=depth))

def flatten(array):
    """
    Flattens array a single level deep.

    Args:
        array (list): List to flatten.

    Returns:
        list: Flattened list.

    Example:

        >>> flatten([[1], [2, [3]], [[4]]])
        [1, 2, [3], [4]]


    .. versionadded:: 1.0.0

    .. versionchanged:: 2.0.0
        Removed `callback` option. Added ``is_deep`` option. Made it shallow
        by default.

    .. versionchanged:: 4.0.0
        Removed ``is_deep`` option. Use :func:`flatten_deep` instead.
    """
    return flatten_depth(array, depth=1)

def flatten_deep(array):
    """
    Flattens an array recursively.

    Args:
        array (list): List to flatten.

    Returns:
        list: Flattened list.

    Example:

        >>> flatten_deep([[1], [2, [3]], [[4]]])
        [1, 2, 3, 4]

    .. versionadded:: 2.0.0
    """
    return flatten_depth(array, depth=-1)
