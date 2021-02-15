import requests as r
import urllib.parse

from config import delivery_cost
from databaser import Databaser as db


api_port = 8080


def get_categories():
    resp = r.get(f'http://localhost:{api_port}/api/categories/')
    if resp.status_code == 200:
        lst = resp.json()
        res = [i['name'] for i in lst]
        return res
    return []


def get_restaurants(category):
    resp = r.get(f'http://localhost:{api_port}/api/categories/{urllib.parse.quote(category)}')
    if resp.status_code == 200:
        lst = resp.json()
        ans = []
        for c in lst:
            ans.append(c['name'])
        return ans
    return []


def get_food_categories(restaurant):
    resp = r.get(f'http://localhost:{api_port}/api/restaurants/{urllib.parse.quote(restaurant)}')
    if resp.status_code == 200:
        lst = resp.json()
        ans = []
        for c in lst:
            ans.append(c['name'])
        return ans
    return []


def get_food_in_foodcat(restaurant, foodcat):
    resp = r.get(f'http://localhost:{api_port}/api/restaurants/{urllib.parse.quote(restaurant)}/{urllib.parse.quote(foodcat)}/')
    if resp.status_code == 200:
        lst = resp.json()
        return lst
    return []


def get_user_cart(uid):
    dbw = db()
    res = []
    cart = dbw.get_user_cart(uid)
    for c in cart:
        resp = r.get(f'http://localhost:{api_port}/api/item/{c[0]}/')
        if resp.status_code == 200:
            details = resp.json()
            details.update({'count': c[1]})
            res.append(details.copy())
            details.clear()
    return res


def get_user_cart_item(uid, item):
    dbw = db()
    count = dbw.get_user_cart_item(uid, item)
    resp = r.get(f'http://localhost:{api_port}/api/item/{item}/')
    if resp.status_code == 200:
        details = resp.json()
        details.update({'count': count})
        return details


def calculate_total_sum(uid):
    ans = 0
    cart = get_user_cart(uid)
    for c in cart:
        ans += int(c['price']) * int(c['count'])
    if ans > 0:
        ans += delivery_cost
    return ans


def add_order_to_api(order_text, total_cost, lat, lon, addr):
    address = ''
    if addr is not None:
        address = addr
    else:
        address = f'https://www.google.com/maps/search/?api=1&query={lat},{lon}'
    payload = {'cost': total_cost, 'details': order_text, 'address': address}
    r.post(f'http://localhost:{api_port}/api/addorder/', data=payload)
