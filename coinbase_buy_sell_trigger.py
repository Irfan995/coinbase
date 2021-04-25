import cbpro
import time
import requests
from datetime import datetime
from coinbase.wallet.client import Client


passphrase = '5wx3wsqwi5q'
b64secret = 'H38KtFytazVZZDVFHRHz9GwruaACjkPpPV6WBflNEalp6SZd8wyEP4xuC2ctuT5avdO3Yfr2vE4aKqTPRJjwAQ=='
key = 'ca4a4b9d543f18c5da1ee9995bfb56ef'

auth_client = cbpro.AuthenticatedClient(key, b64secret, passphrase,
                                api_url="https://api-public.sandbox.pro.coinbase.com")
accounts = auth_client.get_accounts()


# Buying parameters
buy_price = '100.0'
buy_size = '0.01'

# Selling parameters
sell_price = '200.0'
sell_size = '0.01'

def profitable(auth_client):
    ''' Check if it is profitable to sell'''

    bought_btcs = list(auth_client.get_fills(product_id="BTC-USD"))
    current_price_usd = get_current_price(key, b64secret)
    total_bought_btcs = len(bought_btcs)
    
    cost = 0
    for btc in bought_btcs:
        btc_bought_price = btc.get('price')
        cost = cost + float(btc_bought_price) 
    
    avg_cost = cost / total_bought_btcs
    profit = (float(current_price_usd) - avg_cost) * total_bought_btcs
    print(avg_cost, profit)
    if profit > 0:
        profitable = True
    else:
        profitable = False

    return profitable


def get_current_price(key, b64secret):
    '''Returns current price'''

    client = Client(key, b64secret, api_version='YYYY-MM-DD')
    currency_code = 'USD'  # can also use EUR, CAD, etc.
    # Make the request
    price = client.get_spot_price(currency=currency_code)
    print('Current bitcoin price in {}: {}'.format(currency_code, price.amount))
    return price.amount


# inititally 
down = 0
up = 0

threshold = 4 # It can be changed

while(True):
    request = requests.get("https://api.pro.coinbase.com/products/BTC-USD/candles/1m")
    json_lists = request.json()

    latest_time_json = json_lists[0]
    latest_time = datetime.fromtimestamp(latest_time_json[0])
    latest_low = latest_time_json[1]
    latest_high = latest_time_json[2]
    latest_open = latest_time_json[3]
    latest_close = latest_time_json[4]

    if latest_open > latest_close:
        down += 1
        print("Down at {}: {}".format(latest_time, down))
    else:
        up += 1
        print("Up at {}: {}".format(latest_time, up))

    if down >= threshold:
        print("Down direction!")
        # Make sure up and down returns to zero
        up = 0
        down = 0
        
        for account in accounts:
            account_id = account.get('id')
            balance = account.get('balance')
            if float(balance) > 0:
                print("Bought")
                auth_client.buy(price=buy_price, #USD
                                size=buy_size, #BTC
                                order_type='limit',
                                product_id='BTC-USD')
        
    if up >= threshold:
        print("Up direction!")
        # Make sure up and down returns to zero
        up = 0
        down = 0
        is_profitable = profitable(auth_client)
        if is_profitable:
            print("Sold")
            auth_client.sell(price=sell_price, #USD
                            size=sell_size, #BTC
                            order_type='limit',
                            product_id='BTC-USD')
        else:
            print("Not Profitable")

    time.sleep(60) # loop start after one minute
