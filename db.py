import logging
import aiomysql
from settings import config


async def init_connections_pool():
    return await aiomysql.create_pool(**config['mysql'])


async def proceed_orders_table(conn, data):
    ids = tuple({each[0] for each in data})
    data_to_insert = str(data).strip('[]')

    delete_query = f"""
            DELETE FROM orders
            WHERE order_id in {ids}
        """
    insert_query = f"""
            INSERT INTO orders
            VALUES {data_to_insert}
        """
    async with conn.cursor() as cursor:
        result = await cursor.execute(delete_query)
        await conn.commit()
        logging.info(f'Table orders: {result} rows have been deleted')
        result = await cursor.execute(insert_query)
        await conn.commit()
        logging.info(f'Table orders: {result} rows have been added')


async def proceed_session_orders_table(conn, data):
    ids = tuple({each[0] for each in data})
    data_to_insert = str(data).strip('[]')

    delete_query = f"""
           DELETE FROM session_orders
           WHERE order_id IN {ids}
        """
    insert_query = f"""
            INSERT INTO session_orders
            VALUES {data_to_insert}
        """
    async with conn.cursor() as cursor:
        result = await cursor.execute(delete_query)
        await conn.commit()
        logging.info(f'Table session orders: {result} rows have been deleted')
        result = await cursor.execute(insert_query)
        await conn.commit()
        logging.info(f'Table session orders: {result} rows have been added')
