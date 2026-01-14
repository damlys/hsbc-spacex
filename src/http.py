from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import logging
import requests
import sys


class HttpClient:
    def __init__(self):
        self.session = Session()
        retries = Retry(
            total=1,  # one retry
            backoff_factor=15,  # waits 15 seconds for second try
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def get(self, url):
        try:
            response = self.session.get(
                url,
                timeout=15,  # 15 seconds of timeout
            )
            if response.status_code < 200 or response.status_code > 299:  # duplicates "except Exception" but I left it for the exercise purposes
                logging.critical(f"HTTP GET response error, status code: {response.status_code}")
                sys.exit(1)
            response.raise_for_status()
            return response
        except requests.exceptions.RetryError:
            logging.critical(f"HTTP GET retry limit reached")
            sys.exit(1)
        except Exception as e:
            logging.critical(f"HTTP GET unknown error: {e}")
            sys.exit(1)
