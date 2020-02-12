import json
import logging
import requests
import aiohttp
from settings import config
from abc import ABC, abstractmethod
from decorators import ResponseHandler

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


"""
Bridge Pattern
"""


class Floship:
    """
    Abstraction class
    """
    def __init__(self, implementation) -> None:
        self.implementation = implementation

    async def make_request(self, *args, **kwargs):
        return await self.implementation.make_request(*args, **kwargs)


class Implementation(ABC):
    """

    """
    @abstractmethod
    def make_request(self, method, api_url, params):
        pass


class FloshipAPI(Implementation):
    """
    Implementation of the Floship API
    https://admin.floship.com/developers
    """

    config = config["floship_api"]
    headers = {
        'Authorization': f'Token {config["token"]}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    main_url = 'https://admin.floship.com/api/v1/'

    def __init__(self):
        self.url = f'{self.main_url}'

    async def make_request(self, method, api_url, params):
        # return self.session.request(method=method, url=f'{self.url}{api_url}', params=params)
        async with aiohttp.ClientSession(headers=self.headers) as session:
            return await session.request(method=method, url=f'{self.url}{api_url}', params=params)


class FloshipSession(Implementation):
    """
    Implementation of the internal Floship API
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

    # def __init__(self):
    #     self.login()

    def login(self, session):
        """
        Method to retrieve session token for further requests
        :return:
        """
        session.request('POST', url=self.login_url, data=json.dumps(self.payload))

    async def make_request(self, method, url, data=None, params=None):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            self.login(session)
            return await session.request(method=method, url=url, data=data, params=params)

