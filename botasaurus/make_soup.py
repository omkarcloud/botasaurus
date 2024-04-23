from bs4 import BeautifulSoup

def make_soup(item) -> BeautifulSoup:
    # Driver
    if hasattr(item, 'page_html'):
        return BeautifulSoup(item.page_html, 'html.parser')
    # Element
    if hasattr(item, 'html'):
        return BeautifulSoup(item.html, 'html.parser')

    # Text
    if hasattr(item, 'text'):
        return BeautifulSoup(item.text, 'html.parser')
    
    raise ValueError(f"Unable to create BeautifulSoup object for {item}")