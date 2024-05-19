from bs4 import BeautifulSoup

def soupify(item) -> BeautifulSoup:
    # Driver 
    if hasattr(item, 'page_html'):
        return BeautifulSoup(item.page_html, 'html.parser')
    # Element
    if hasattr(item, 'html'):
        return BeautifulSoup(item.html, 'html.parser')

    # Text
    if hasattr(item, 'text'):
        return BeautifulSoup(item.text, 'html.parser')

    if isinstance(item, str):
        return BeautifulSoup(item, 'html.parser')

    if isinstance(item, dict):
        raise ValueError(f"Unable to create BeautifulSoup object for dicts")

    if item is None:
        raise ValueError(f"Unable to create BeautifulSoup object for None")

    raise ValueError(f"Unable to create BeautifulSoup object for {item}")