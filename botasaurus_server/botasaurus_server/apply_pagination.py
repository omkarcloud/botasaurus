def apply_pagination(data, page, per_page, hidden_fields=None):
    """
    Paginate the data based on page and per_page, providing detailed pagination information.

    :param data: The list of items to paginate.
    :param page: The page number of the results to return.
    :param per_page: The maximum number of items to return per page. Can be None to return all items.
    :return: A dictionary containing the count, total_pages, next, previous, and results.
    """
    count = len(data)
    
    # Handle the case where per_page is None - return all items
    if per_page is None:
        per_page = 1 if count == 0 else count 
        page = 1

    # Calculate the total number of pages
    total_pages = max((count + per_page - 1) // per_page, 1)  # Ensure at least 1 page
    page = max(min(page, total_pages), 1)  # Ensure page is within valid range
    # Calculate indices for slicing the data list to get the current page of results
    start = (page - 1) * per_page
    end = min(start + per_page, count)

    # Determine the page numbers for the next and previous pages
    next_page = page + 1 if end < count else None
    previous_page = page - 1 if start > 0 else None

    # Prepare the paginated results
    results = data[start:end]

    # Construct the next and previous page information
    next_info = {"page": next_page, "per_page": per_page} if next_page is not None else None
    previous_info = {"page": previous_page, "per_page": per_page} if previous_page is not None else None

    # Construct the response dictionary
    
    
    pagination_info = {
        "count": count,
        "total_pages": total_pages,
        "next": next_info,
        "previous": previous_info,
        "results": results,        
    }

    if hidden_fields is not None:
        pagination_info["hidden_fields"] =hidden_fields

    return pagination_info
