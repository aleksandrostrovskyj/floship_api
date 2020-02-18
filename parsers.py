from datetime import datetime


def parse_date(date_field):
    if date_field:
        try:
            date_format = datetime.strptime(date_field, '%Y-%m-%dT%H:%M:%S.%f%z')
            return date_format.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            date_format = datetime.strptime(date_field, '%Y-%m-%dT%H:%M:%S%z')
            return date_format.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return ''


def parse_api_response_orders(page):

    def parse_courier(courier_node):
        if courier_node:
            return courier_node['courier_id'], courier_node['name']
        else:
            return '', ''

    return [
        (
            order['order_id'],
            parse_date(order['original_transaction_date']),
            line['customs_value']['amount'],
            line['customs_value']['currency'],
            line['quantity'],
            line['item_id'],
            line['product_id'],
            line['has_batteries'],
            line['customs_description'],
            line['gross_width'],
            line['description'],
            line['gross_weight'],
            line['product_quantity'],
            line['packaging_type'],
            line['harmonized_code'],
            line['item_type'],
            line['upc'],
            line['gross_length'],
            line['customs_category'],
            line['country_of_manufacture'],
            line['sku'],
            line['gross_height'],
            order['shipping_address']['country'] or '',
            order['shipping_address']['addressee'] or '',
            order['shipping_address']['address_1'] or '',
            order['shipping_address']['address_2'] or '',
            order['shipping_address']['address_3'] or '',
            order['shipping_address']['city'] or '',
            order['shipping_address']['state'] or '',
            order['shipping_address']['postal_code'] or '',
            order['shipping_address']['company'] or '',
            order['shipping_address']['phone'] or '',
            order['shipping_address']['email'] or '',
            order['status'],
            order['customer_reference'],
            order['reference'],
            parse_date(order['create_date']),
            parse_date(order['update_date']),
            parse_date(order['approval_eligibility_date']),
            *parse_courier(order['courier']),
            order['tracking_number'],
            order['tracking_url'],
            order['customer_shipping_option'],
            order['commercial_invoice'] or '',

        )
        for order in page
        for line in order['order_lines']
    ]


def parse_session_response_order(order):

    def parse_courier(courier_node):
        if courier_node:
            return (
                courier_node['id'],
                courier_node['display_name'],
                courier_node['courier_type'],
                courier_node['courier_type_name']
            )
        else:
            return '', '', '', ''

    def parse_costs(costs_node):
        if costs_node:
            return (
                costs_node['sales_order_id'],
                costs_node['pick_pack_cost'] or 0,
                costs_node['actual_cost'] or 0,
                costs_node['fuel_surcharge'] or 0,
                costs_node['actual_weight'] or 0,
                costs_node['processing_fee'] or 0,
                costs_node['estimated_shipping_cost'] or 0,
                costs_node['estimated_pick_pack_cost'] or 0,
                costs_node['return_cost'] or 0,
                costs_node['discount_value'] or 0
            )
        else:
            return 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

    return (
        order['id'],
        order['status'],
        order['source'],
        order['exception_code'] or '',
        order['client_po'],
        order['floship_so_number'],
        parse_date(order['create_date']),
        *parse_courier(order['ship_via']),
        order['tracking_number'],
        *parse_costs(order['cost']),
        order['parent_order'] or ''
    )
