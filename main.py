from floship import Floship, FloshipAPI, FloshipSession
from parsers import parse_api_response_order, parse_session_response_order
from db import db_create_engine, insert_data, delete_data
from datetime import date, timedelta
import logging
from pathlib import Path

BASE_DIR = Path(__file__).parent

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename=BASE_DIR / 'orders.log')


def main_api(date_from: date):
    floship_api = Floship(FloshipAPI())
    api_url = 'orders/'
    api_params = {
        'limit': 150,
        'page': 1,
        'create_date_from': date.strftime(date_from, '%Y-%m-%dT00:00:00')
    }

    result = []
    while True:
        response = floship_api.make_request('GET', api_url, api_params)
        for each in response.json()['results']:
            result.extend(parse_api_response_order(each))

        if not response.json()['next']:
            break

        api_params['page'] += 1
    ids_list = tuple([each[0] for each in result])
    engine = db_create_engine()
    delete_data(engine, ids_list, 'orders')
    insert_data(engine, result, 'orders')


def main_session(date_from):
    floship_session = Floship(FloshipSession())
    session_url = 'https://admin.floship.com/internal_api/orders/'
    session_params = {
        'order_type__in': 'stock,crossdocking,parcel_forwarding',
        'sort_by': '-create_date',
        'create_date_from': date.strftime(date_from, '%Y-%m-%dT00:00:00'),
        'page': 1,
        'limit': 150
    }

    result = []
    while True:
        response = floship_session.make_request('GET', session_url, params=session_params)
        for each in response.json()['results']:
            result.append(parse_session_response_order(each))

        if not response.json()['next']:
            break

        session_params['page'] += 1
    ids_list = tuple([each[0] for each in result])
    engine = db_create_engine()
    delete_data(engine, ids_list, 'session_orders')
    insert_data(engine, result, 'session_orders')


if __name__ == '__main__':
    date_from = date.today() - timedelta(days=30)
    main_api(date_from)
    main_session(date_from)


