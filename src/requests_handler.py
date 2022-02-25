import logging
import time
from datetime import datetime
from fake_useragent import UserAgent
import requests

_LOGGER = logging.getLogger('RequestsHandler')
_USER_AGENT = UserAgent().chrome  # Use chrome agent otherwise metacritic.com gets angry and returns 403
_HEADERS = {'User-Agent': _USER_AGENT}


class RequestHandler:

    def __init__(self, politeness_interval_ms, timeout_secs=10):
        """
        Constructor for RequestsHandler
        :param politeness_interval_ms: minimum time interval between each request
        :param timeout_secs: timeout of
        """
        self._last_request_time = None
        self._politeness_interval_ms = politeness_interval_ms
        self._timeout_secs = timeout_secs

    def _send_get_request(self, url: str):
        """
        Sends get request to the specified url and sets _last_request_time to current date and time
        :param url: url to send get request to
        :return: response from http get
        """
        _LOGGER.debug(f'Sending get request to url: {url}')
        res = requests.get(url, timeout=self._timeout_secs, headers=_HEADERS)
        self._last_request_time = datetime.now()
        return res

    def get(self, url: str):
        """
        Sends get request to the specified url, following the specified politeness_interval_ms passed in the constructor
        Suspends current thread for the remaining duration if necessary
        :param url: url to send get to
        :return: response
        """
        if self._last_request_time is None:
            return self._send_get_request(url)

        diff_ms = (datetime.now() - self._last_request_time).total_seconds() * 1000
        if diff_ms < self._politeness_interval_ms:
            # sleep for the remaining duration (approx)
            sleep_time = self._politeness_interval_ms - diff_ms
            time.sleep(sleep_time / 1000)

        # Finally, send the actual request
        return self._send_get_request(url)
