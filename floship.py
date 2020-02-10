import json
import pickle
import logging
import requests
import functools
from settings import config
from datetime import datetime

logging.basicConfig(format='%(asctime)s - %(cor_func_name)s - %(levelname)s - %(message)s', level=logging.INFO)


class ResponseHandler:
    """
    Class implementing a response processing decorator
    """
    @classmethod
    def handler(cls, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log_extra = {'cor_func_name': func.__name__}
            try:
                logging.info('Send request.', extra=log_extra)
                response = func(*args, **kwargs)
                logging.info('Check status.', extra=log_extra)
                response.raise_for_status()
            except requests.exceptions.HTTPError as http_error:
                logging.warning(f'{http_error} - Issue with request', extra=log_extra)
            except Exception as exc:
                logging.warning(f'{exc} - issue in program', extra=log_extra)
            else:
                logging.info(f'OK - {response}', extra=log_extra)
                return response
        return wrapper


class FloshipBaseApi:
    """
    Base class
    """
    config = config["floship_api"]
    headers = {
        'Authorization': f'Token {config["token"]}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    main_url = 'https://admin.floship.com/api/v1/{}'

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    @ResponseHandler.handler
    def make_request(self, *args, **kwargs):
        request_url = self.main_url.format(kwargs.pop('api_url'))
        return self.session.request(*args, url=request_url, headers=self.headers, **kwargs)


class FloshipAPI(FloshipBaseApi):
    """
    Class for each API entity realizing
    """
    def list_orders(self, params={}):
        params = {
            'page': 1,
            'limit': 50,
            **params
        }

        while True:
            response = self.make_request(method='GET', api_url='orders/', params=params)
            yield response

            if not response.json()['next']:
                # If no pagination - exit loop
                break

            params['page'] += 1


class FloshipBaseSession:
    """
    Base class for Session requests (internal Floship API)
    Main reason: not all information exists in regular API
    Should only be used for cost information retrieving.
    """
    login_url = 'https://admin.floship.com/internal_api/users/login'
    config = config["floship_api"]
    headers = {
        'accept': "application/json, text/plain, */*",
        'sec-fetch-dest': "empty",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36",
        'content-type': "application/json;charset=UTF-8",
        'cache-control': "no-cache",
    }

    payload = {
        'username': config['username'],
        'password': config['password']
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.login()

    @ResponseHandler.handler
    def login(self):
        return self.session.request('POST', url=self.login_url, data=json.dumps(self.payload))

    @ResponseHandler.handler
    def make_request(self, *args, **kwargs):
        return self.session.request(*args, **kwargs)


class FloshipSession(FloshipBaseSession):
    """
    Class to retrieve data via internal Floship API
    """
    def list_orders(self, date_from: datetime = ''):
        """
        Main purpose - retreive cost information
        :param date_from: start date of order creation
        :return: <class 'requests.models.Response'>
        """
        url = 'https://admin.floship.com/internal_api/orders/'
        params = {
            'order_type__in': 'stock,crossdocking,parcel_forwarding',
            'sort_by': '-create_date',
            'page': 1
        }

        if date_from:
            # Date to string conversion
            str_date_from = date_from.strftime('%Y-%m-%dT00:00:00')
            params['create_date_from'] = str_date_from

        while True:
            response = self.make_request(method='GET', url=url, params=params)
            yield response

            if not response.json()['next']:
                # If no pagination - exit loop
                break

            params['page'] += 1

        self.session.close()


def test_api():
    f = FloshipAPI()
    count = 0
    for page in f.list_orders():
        count += 1
        json_data = json.dumps(page.json(), indent=3)
        with open(f'test_results\\api_floship_{count}.json', 'w') as f:
            f.writelines(json_data)

        with open(f'test_results\\api_floship_{count}.pickle', 'wb') as f:
            pickle.dump(file=f, obj=page)


def test_session():
    f = FloshipSession()
    count = 0
    for page in f.list_orders():
        count += 1
        json_data = json.dumps(page.json(), indent=3)
        with open(f'test_results\\session_orders_response_{count}.pickle', 'wb') as f:
            pickle.dump(file=f, obj=page)

        with open(f'test_results\\session_orders_response_{count}.json', 'w') as f:
            f.writelines(json_data)
