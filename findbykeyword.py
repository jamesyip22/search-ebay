#!/usr/bin/env python3
from ebaysdk.finding import Connection
import schedule
import time
import telegram_send

history = []
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

def search_ebay():
    global history
    response = api.execute('findItemsByKeywords', request)
    for item in response.reply.searchResult.item:
        if item.itemId not in history:
            #print(f"{item.title} -- {item.sellingStatus.currentPrice.value} ------ {item.viewItemURL}")
            telegram_send.send(messages = [f"${item.sellingStatus.currentPrice.value} --- {item.viewItemURL}"] )
            history.append(item.itemId)

schedule.every(1).minutes.do(search_ebay)

while True:
    schedule.run_pending()
    time.sleep(1)
