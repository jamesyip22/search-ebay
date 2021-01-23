#!/usr/bin/env python3
from ebaysdk.finding import Connection
import schedule
import time
import telegram_send
import re
import pickle
import os.path
import requests
from bs4 import BeautifulSoup
import cchardet

api = Connection(config_file='ebay.yaml', siteid="EBAY-US")
request = {
    'keywords': 'search item',
    'itemFilter': [
        {
            'name': 'ListingType',
            'value': ['FixedPrice', 'AuctionWithBIN']
        },
        {
            'name': 'LocatedIn',
            'value': 'US'
        },
        {
            'name': 'MinQuantity',
            'value': '1'
        },
        {
            'name': 'MaxPrice',
            'value': '210.00'
        },
        {
            'name': 'MinPrice',
            'value': '55.00'
        },
        {
            'name': 'Condition',
            'value': ['1000', '1500', '2000', '2500', '2750', '3000', '4000', '5000', '6000']
        }
    ],
    'paginationInput': {
        'entriesPerPage': 100,
        'pageNumber': 1
    },
    'sortOrder': 'PricePlusShippingLowest'
}

filename = "rick.pkl"

def start():
    global history
    if os.path.exists(filename):
        with open(filename, 'rb') as file:
            history = pickle.load(file)
    else:
        history = []
            
def save():
    with open(filename, 'wb') as file:
        pickle.dump(history, file)


def search_ebay():
    response = api.execute('findItemsByKeywords', request)
    if int(response.reply.paginationOutput.totalPages) > 1:
        telegram_send.send(messages = [f"**Warning** Total pages: {response.reply.paginationOutput.totalPages}"] )
    for item in response.reply.searchResult.item:
        if item.itemId not in history:
            url = item.viewItemURL
            session = requests.Session()
            soup = BeautifulSoup(session.get(url).text, 'lxml')
            soup2 = BeautifulSoup(session.get(soup.find(id='desc_ifr')['src']).text, 'lxml')
            desc = soup2.find('div', id='ds_div').find_all('p')
            telegram_send.send(messages = [f"${price} --- {desc[0].text} \n {url}"] )
            history.append(item.itemId)

schedule.every(1).minutes.do(search_ebay)

try:
    start()
    telegram_send.send(messages = ["Bot started."] )
    while True:
        schedule.run_pending()
        time.sleep(1)
finally:
    save()
    telegram_send.send(messages = ["Bot stopped - Progress saved."] )
