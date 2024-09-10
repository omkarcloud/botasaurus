from bs4 import BeautifulSoup


def soupify(item) -> BeautifulSoup:

    if isinstance(item, str):
        return BeautifulSoup(item, "html.parser")
    elif isinstance(item, BeautifulSoup):
        return item
    # Driver
    elif hasattr(item, "page_html"):
        return BeautifulSoup(item.page_html, "html.parser")
    # Element
    elif hasattr(item, "html"):
        return BeautifulSoup(item.html, "html.parser")

    # Text
    elif hasattr(item, "text"):
        return BeautifulSoup(item.text, "html.parser")

    elif isinstance(item, dict):
        raise ValueError(f"Unable to create BeautifulSoup object for dicts")

    elif item is None:
        raise ValueError(f"Unable to create BeautifulSoup object for None")
    else:
        raise ValueError(f"Unable to create BeautifulSoup object for {item}")
