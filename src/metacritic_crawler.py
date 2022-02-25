import logging
from typing import List

from src.html_parser import HtmlParser
from src.metacritic_item_crawler import MetacriticItemCrawler
from src.metacritic_uri_builder import create_games_url, create_movies_url, create_absolute_item_url
from src.requests_handler import RequestHandler

# Module logger
_LOGGER = logging.getLogger('MetacriticCrawler')

# Xpath config
_XPATH_CONFIG = {
    'itemUriXPath': "//div[contains(@class, 'browse_list_wrapper')]" +
                    "//td[contains(@class, 'clamp-summary-wrap')]//a[contains(@class, 'title')]/@href",
    'maxPageXPath': "//li[contains(@class, 'page last_page')]" +
                    "//a[contains(@class, 'page_num')]/text()",
    'criticScoreXPath': "//span[@itemprop='ratingValue']",
    'userScoreXPath': "//div[contains(@class,'userscore_wrap feature_userscore')]" +
                      "//div[contains(@class, 'metascore_w user')]/text()"
}


class MetacriticCrawlerConfig:

    def __init__(self, games_years: List[int] | None, movies_years: List[int] | None,
                 politeness_interval_ms: int = 500):
        """
        Config for metacritic crawler
        :param games_years: list of years to download from
        :param movies_years: all years that will be crawled
        """
        self.games_years = games_years
        self.movies_years = movies_years
        self.politeness_interval_ms = politeness_interval_ms


class MetacriticCrawler:
    """
    Class for simple metacritic.com crawling.
    Crawls games and movies for specified years and extracts their description with metascores and reviews
    """
    DEFAULT_CONFIG = MetacriticCrawlerConfig(games_years=[2010 + x for x in range(12)],
                                             movies_years=[2012 + x for x in range(10)])

    def __init__(self, config: MetacriticCrawlerConfig):
        """
        Default constructor
        :param config: config object
        """
        self._config = config
        self._req_handler = RequestHandler(config.politeness_interval_ms)

    def crawl(self):
        games_years, movies_years = self._config.games_years, self._config.movies_years
        crawled_games, crawled_movies = {}, {}

        if games_years is not None:
            self._crawl_content('games', games_years, crawled_games)

        if movies_years is not None:
            self._crawl_content('movies', movies_years, crawled_movies)

        return {'games': crawled_games, 'movies': crawled_movies}

    def _crawl_content(self, content_name: str, games_years, store):
        for year in games_years:
            _LOGGER.info(f'Crawling {content_name} released in {year}')
            store[year] = self._crawl_year(year=year,
                                           create_url_fn=create_games_url
                                           if content_name == 'games'
                                           else create_movies_url, crawl_item_fn=self._crawl_game_item)

    def _crawl_year(self, year, create_url_fn, crawl_item_fn):
        """
        Crawls all items from the given year
        :param year: year
        :param create_url_fn: factory function to create a string url
        :param crawl_item_fn: function to crawl item info
        :return:
        """
        max_page = None
        current_page = 0

        uri = create_url_fn(year)
        scraped_items = []

        while not current_page == max_page:
            # create new parser
            res = self._req_handler.get(uri)
            document_parser = HtmlParser(res)

            # Check whether the document is parseable - if not return scraped_items
            if not document_parser.is_document_parseable():
                _LOGGER.error(f'Error could not GET url: {uri}, skipping ...')
                return scraped_items

            # If we have not checked the max page yet check it
            if max_page is None:
                max_page = document_parser.find_items(_XPATH_CONFIG['maxPageXPath'])
                if len(max_page) == 0:
                    break
                else:
                    max_page = int(max_page[0])

            # Get all item urls
            item_urls = document_parser.find_items(_XPATH_CONFIG['itemUriXPath'])
            _LOGGER.debug(f'Found {len(item_urls)} item urls, attempting to scrape ...')

            # Process all item urls
            for relative_item_url in item_urls:
                processed_item = crawl_item_fn(create_absolute_item_url(relative_item_url))
                return scraped_items  # todo remove
                if processed_item is not None:
                    scraped_items.append(processed_item)

            current_page += 1

        return scraped_items

    def _crawl_game_item(self, item_url):
        res = self._req_handler.get(item_url)
        document_parser = HtmlParser(res)

        if not document_parser.is_document_parseable():
            _LOGGER.error(f'Error could not GET url: {item_url}, skipping ...')
            return None

        crawler = MetacriticItemCrawler(document_parser, item_url, self._req_handler)
        return crawler.crawl()


crawler = MetacriticCrawler(MetacriticCrawlerConfig(games_years=[2021], movies_years=None))
items = crawler.crawl()
print('')
