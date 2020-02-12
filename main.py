from floship import Floship, FloshipSession, FloshipAPI
import asyncio
from time import time


async def main():
    floship_api = Floship(FloshipAPI())
    api_url = 'orders/'
    params = {
        'limit': 10,
        'page': 1
    }
    result = []

    while True:
        response = await asyncio.create_task(floship_api.make_request('GET', api_url, params))
        data = await response.json()
        result.extend(data['results'])
        params['page'] += 1
        print(data['next'])
        if not data['next']:
            break

    print(len(result))


async def main2():
    floship_session = Floship(FloshipSession())
    url = 'https://admin.floship.com/internal_api/orders/'
    params = {
        'order_type__in': 'stock,crossdocking,parcel_forwarding',
        'sort_by': '-create_date'
    }

    result = []

    while True:
        response = await asyncio.create_task(floship_session.make_request('GET', url, params))
        data = await response.json()
        result.extend(data['results'])
        params['page'] += 1
        print(data['next'])
        if not data['next']:
            break

    print(len(result))

if __name__ == '__main__':
    t0 = time()
    asyncio.run(main2())
    print(time() - t0)
