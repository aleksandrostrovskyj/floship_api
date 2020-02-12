from settings import config
from sqlalchemy import (
    create_engine,
    MetaData, Table, Column,
    BigInteger, Integer, DateTime,
    Float, String, Boolean
)
import logging

meta = MetaData()

orders = Table(
    'orders', meta,
    Column('order_id', BigInteger, nullable=False),
    Column('original_transaction_date', DateTime, nullable=False),
    Column('amount', Float),
    Column('currency', String(5)),
    Column('quantity', Integer),
    Column('item_id', BigInteger),
    Column('product_id', BigInteger),
    Column('has_batteries', Boolean),
    Column('customs_description', String(200)),
    Column('gross_width', Float),
    Column('description', String(200)),
    Column('gross_weight', Float),
    Column('product_quantity', Integer),
    Column('packaging_type', String(100)),
    Column('harmonized_code', String(100)),
    Column('item_type', String(100)),
    Column('upc', String(100)),
    Column('gross_length', Float),
    Column('customs_category', String(100)),
    Column('country_of_manufacture', String(10)),
    Column('sku', String(20)),
    Column('gross_height', Float),
    Column('shipping_country', String(10)),
    Column('shipping_addressee', String(100)),
    Column('shipping_address_1', String(100)),
    Column('shipping_address_2', String(100)),
    Column('shipping_address_3', String(100)),
    Column('shipping_city', String(50)),
    Column('shipping_state', String(50)),
    Column('shipping_postal_code', String(50)),
    Column('shipping_company', String(50)),
    Column('shipping_phone', String(20)),
    Column('shipping_email', String(50)),
    Column('status', String(50)),
    Column('customer_reference', String(50)),
    Column('reference', String(50)),
    Column('order_create_date', DateTime),
    Column('order_update_date', DateTime),
    Column('approval_eligibility_date', DateTime),
    Column('courier_id', Integer),
    Column('courier_name', String(50)),
    Column('tracking_number', String(200)),
    Column('tracking_url', String(200)),
    Column('customer_shipping_option', String(100)),
    Column('commercial_invoice', String(200))
)


def db_create_engine():
    dsn = "mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    db_url = dsn.format(**config['mysql'])
    return create_engine(db_url)


def insert_data(engine, data, table):
    data_to_insert = str(data).strip('[]')
    query = f"""
        INSERT INTO {table}
        VALUES {data_to_insert}
    """
    result = engine.execute(query)
    logging.info(f'Table {table}: {result.rowcount} rows have been added')
    result.close()


def delete_data(engine, ids_list, table):
    query = f"""
            DELETE FROM {table}
            WHERE order_id in {ids_list}
        """
    result = engine.execute(query)
    logging.info(f'Table {table}: {result.rowcount} rows have been deleted')
    result.close()
