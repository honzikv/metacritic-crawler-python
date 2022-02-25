# Module for metacritic html parsing
from requests import Response
from lxml import html


class HtmlParser:

    def __init__(self, res: Response):
        html_page = HtmlParser.parse_html(res)
        self._html_page = None if html_page is None else html.fromstring(html_page)

    @staticmethod
    def parse_html(res: Response) -> str | None:
        """
        Tries parsing html from http response. If the response is not 200 or text is not present the function returns False
        :param res: http response
        :return: parsed html or False
        """
        return res.text if res.status_code == 200 and res.text is not None else None

    def is_document_parseable(self):
        return self._html_page is not None

    def find_items(self, xpath: str):
        """
        Parses all items by xpath and returns them in a list
        :param xpath:
        :return:
        """
        return self._html_page.xpath(xpath)

    def find_item(self, xpath: str):
        """
        Returns first item that matches the xpath string
        :param xpath: xpath string
        :return: first item found or None if no item matching such xpath exists
        """
        items = self._html_page.xpath(xpath)
        return items[0] if len(items) > 0 else None


class ElementParser:
    """
    Util class for element parsing
    """

    def __init__(self, html_element):
        self._element = html_element

    def find_items(self, xpath: str):
        return self._element.xpath(xpath)

    def find_item(self, xpath: str):
        items = self._element.xpath(xpath)
        return items[0] if len(items) > 0 else None

