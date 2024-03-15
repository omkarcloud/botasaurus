
def apply_offset_limit(data, offset, limit):
    """
    Paginate the data based on offset and limit, providing detailed pagination information.

    :param data: The list of items to paginate.
    :param offset: The starting position in the data list.
    :param limit: The maximum number of items to return.
    :return: A dictionary containing the count, page_count, next, previous, and results.
    """
    # Calculate the total number of items and the total number of pages
    count = len(data)
    page_count = max((count + limit - 1) // limit, 1)  # Ensure at least 1 page

    # Calculate indices for slicing the data list to get the current page of results
    start = offset
    end = min(offset + limit, count)

    # Determine the next and previous offsets
    next_offset = None if end >= count else end
    # next_offset = end if end < count else None 

    previous_offset = start - limit if start > 0 else None

    # Prepare the paginated results
    results = data[start:end]

    # Construct the next and previous page information
    next_info = (
        {"offset": next_offset, "limit": limit} if next_offset is not None else None
    )
    previous_info = (
        {"offset": previous_offset, "limit": limit}
        if previous_offset is not None and previous_offset >= 0
        else None
    )

    # Construct the response dictionary
    pagination_info = {
        "count": count,
        "page_count": page_count,
        "next": next_info,
        "previous": previous_info,
        "results": results,
    }

    return pagination_info
