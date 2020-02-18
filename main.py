from time import time
import asyncio
import logging
from datetime import date, timedelta
from floship import Floship, FloshipSession, FloshipAPI
from parsers import parse_api_response_orders, parse_session_response_order
from db import init_connections_pool, proceed_orders_table, proceed_session_orders_table


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


async def floship_orders_api(db_conn_pool, QUEUE, date_from):
    floship_api = Floship(FloshipAPI())
    api_url = 'orders/'
    params = {
        'limit': 5,
        'page': 1,
        'update_date_from': date.strftime(date_from, '%Y-%m-%dT00:00:00')
    }

    while True:
        response = await floship_api.make_request('GET', api_url, params)
        response_page = await response.json()
        parsed_data = parse_api_response_orders(response_page['results'])
        ids = tuple({each[0] for each in parsed_data})

        await QUEUE.put(ids)

        async with db_conn_pool.acquire() as conn:
            await proceed_orders_table(conn, parsed_data)

        if not response_page['next']:
            break
        params['page'] += 1

    await QUEUE.put(None)


async def floship_orders_session(floship_session, order_id):
    session_url = f'https://admin.floship.com/internal_api/orders/{order_id}'
    response = await floship_session.make_request('GET', session_url)
    return await response.json()


async def procces_1(db_conn_pool, QUEUE):
    floship_session = Floship(FloshipSession())

    while True:
        orders_ids = await QUEUE.get()

        if orders_ids is None:
            logging.info('QUEUE is empty. Finish.')
            break

        tasks = []
        for each in orders_ids:
            tasks.append(asyncio.create_task(floship_orders_session(floship_session, each)))

        session_orders_list = await asyncio.gather(*tasks)
        parsed_data = [parse_session_response_order(each) for each in session_orders_list]

        async with db_conn_pool.acquire() as conn:
            await proceed_session_orders_table(conn, parsed_data)

        QUEUE.task_done()
        await asyncio.sleep(2)


async def main():
    QUEUE = asyncio.Queue()
    pool = await init_connections_pool()
    date_from = date.today() - timedelta(days=1)
    prod_task = asyncio.create_task(floship_orders_api(pool, QUEUE, date_from))
    work_task = asyncio.create_task(procces_1(pool, QUEUE))
    await asyncio.gather(prod_task, work_task)


if __name__ == '__main__':
    asyncio.run(main())
