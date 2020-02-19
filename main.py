import asyncio
import logging
from datetime import date, timedelta
from floship import Floship, FloshipSession, FloshipAPI
from parsers import parse_api_response_orders, parse_session_response_order
from db import init_connections_pool, proceed_orders_table, proceed_session_orders_table


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


async def floship_orders_api(db_conn_pool, QUEUE, date_from):
    """
    Producer function - retrieve orders data via Floship API and put orders ids tuple to the QUEUE;
    Write orders to database.
    :param db_conn_pool: pool of MySQL db connections, will be used to write data to the db
    :param QUEUE: will be used to exchange data between producer and consumer functions
    :param date_from: param for Floship API - date from orders were updated
    :return: None
    """
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


async def floship_session_request(floship_session, order_id):
    """
    Function to retrieve data of order_id Floship order via FloshipSession() implementation
    :param floship_session: Floship(FloshipSession()) class instance
    :param order_id: internal id of the Floship's order
    :return: order data in json format
    """
    # Add sleep to avoid Floship server overload
    await asyncio.sleep(1)
    session_url = f'https://admin.floship.com/internal_api/orders/{order_id}'
    response = await floship_session.make_request('GET', session_url)
    return await response.json()


async def floship_orders_session(db_conn_pool, QUEUE):
    """
    Consumer function - check QUEUE for orders ids tuple and retrieve order data via FloshipSession() implementation;
    Write orders data to database.
    :param db_conn_pool: pool of MySQL db connections, will be used to write data to the db
    :param QUEUE: will be used to exchange data between producer and consumer functions
    :return: None
    """
    floship_session = Floship(FloshipSession())

    while True:
        orders_ids = await QUEUE.get()

        if orders_ids is None:
            logging.info('QUEUE is empty. Finish.')
            break

        session_orders_list = []
        for order_id in orders_ids:
            session_orders_list.append(await floship_session_request(floship_session, order_id))

        parsed_data = [parse_session_response_order(each) for each in session_orders_list]

        async with db_conn_pool.acquire() as conn:
            await proceed_session_orders_table(conn, parsed_data)

        QUEUE.task_done()
        await asyncio.sleep(2)


async def main():
    """
    Main async function.
    Initialize
        QUEUE - async queue object;
        pool - pool of MySQL db connections
    Create producer and consumer tasks
    Run them concurrently
    :return:
    """
    QUEUE = asyncio.Queue()
    pool = await init_connections_pool()
    date_from = date.today() - timedelta(days=1)
    prod_task = asyncio.create_task(floship_orders_api(pool, QUEUE, date_from))
    work_task = asyncio.create_task(floship_orders_session(pool, QUEUE))
    await asyncio.gather(prod_task, work_task)


if __name__ == '__main__':
    asyncio.run(main())
