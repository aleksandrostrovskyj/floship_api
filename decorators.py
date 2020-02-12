import logging
import requests
import functools


class ResponseHandler:
    """
    Class implementing a response processing decorator
    """
    @classmethod
    def handler(cls, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logging.info('Send request.')
                response = func(*args, **kwargs)
                logging.info('Check status.')
                response.raise_for_status()
            except requests.exceptions.HTTPError as http_error:
                logging.warning(f'{http_error} - Issue with request')
            except Exception as exc:
                logging.warning(f'{exc} - issue in program')
            else:
                logging.info(f'OK - {response.status_code}')
                return response
        return wrapper
