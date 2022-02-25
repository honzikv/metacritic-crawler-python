# Module for crawling game specific information
import abc
import logging

from src.html_parser import HtmlParser, ElementParser
from src.metacritic_uri_builder import create_critic_reviews_url, create_user_reviews_url
from src.requests_handler import RequestHandler

_LOGGER = logging.getLogger(__name__)

_NAME = "//div[contains(@class, 'product_title')]//a//h1/text()"
_SUMMARY_DETAILS_PUBLISHER = "//div[contains(@class, 'product_data')]//ul[@class='summary_details']"
_METACRITIC_RATING = "//div[contains(@class, 'score_summary') and contains(@class, 'metascore_summary')]" \
                     "//span[@itemprop='ratingValue']/text()"
_USER_RATING = "//a[@class='metascore_anchor']//div[contains(@class, 'metascore_w') and contains(@class,'user')]/text()"

_CRITIC_REVIEWS_XPATHS = {
    'review_list': "//ol[contains(@class, 'reviews') and contains(@class, 'critic_reviews')]//li""//div["
                   "@class='review_content']",
    'reviewer_name': ".//div[@class='review_critic']//div[@class='source']/a",
    'date_reviewed': ".//div[@class='review_critic']//div[@class='date']",
    'score': ".//div[@class='review_grade']/div",
    'review_text': ".//div[@class='review_body']"
}

_USER_REVIEWS_XPATHS = {
    'review_list': "//ol[contains(@class, 'reviews') and contains(@class, 'user_reviews')]//li"
                   "//div[@class='review_content']",
    'review_text': ".//span[contains(@class, 'blurb') and contains(@class, 'blurb_expanded')]",
    'reviewer_name': ".//div[@class='review_critic']//div[@class='name']//a",
    'date_reviewed': ".//div[@class='review_critic']//div[@class='date']",
    'score': ".//div[@class='review_grade']//div"
}


class ItemCrawler:
    def __init__(self, html_parser: HtmlParser, url: str, req_handler: RequestHandler):
        self._req_handler = req_handler
        self._html_parser = html_parser
        self._url = url
        self.result = {}


class MetacriticItemCrawler(ItemCrawler):

    def crawl(self):
        self._get_basic_info()
        self.result['reviews'] = MetacriticReviewCrawler(self._html_parser, self._url, self._req_handler).crawl()

        return self.result

    def _get_basic_info(self):
        name = self._html_parser.find_item(_NAME)
        metacritic_rating = self._html_parser.find_item(_METACRITIC_RATING)
        user_rating = self._html_parser.find_item(_USER_RATING)

        if name is None or not isinstance(name, str):
            # Name must always be present
            _LOGGER.error(f'Error name is missing, cannot crawl this item: {self._url}')

        self.result['name'] = name
        self.result['metacriticRating'] = metacritic_rating
        self.result['userRating'] = user_rating

        print(self.result)


class MetacriticReviewCrawler(ItemCrawler):

    def crawl(self):
        critic_reviews_url = create_critic_reviews_url(self._url)
        user_reviews_url = create_user_reviews_url(self._url)

        self._parse_reviews('criticReviews', critic_reviews_url, _CRITIC_REVIEWS_XPATHS)
        self._parse_reviews('userReviews', user_reviews_url, _USER_REVIEWS_XPATHS)

        return self.result

    def _parse_reviews(self, field_name, url, xpaths):
        reviews_parser = HtmlParser(self._req_handler.get(url))
        if not reviews_parser.is_document_parseable():
            _LOGGER.debug(f'Could not fetch reviews for url: {self._url}')
            return

        reviews = reviews_parser.find_items(xpaths['review_list'])

        def get_text_content_or_none(el_parser, xpath_field):
            val = el_parser.find_item(xpaths[xpath_field])
            return None if val is None else val.text_content()

        mapped_reviews = []
        for review_el in reviews:
            element_parser = ElementParser(review_el)
            mapped_reviews.append({
                'reviewerName': get_text_content_or_none(element_parser, 'reviewer_name'),
                'dateReviewed': get_text_content_or_none(element_parser, 'date_reviewed'),
                'score': get_text_content_or_none(element_parser, 'score'),
                'reviewText': get_text_content_or_none(element_parser, 'review_text')
            })

        self.result[field_name] = mapped_reviews
