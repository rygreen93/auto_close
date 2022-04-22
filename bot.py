import time
import json
import pprint
from pybit import usdt_perpetual


file = open('api.json')
data = json.load(file)

session = usdt_perpetual.HTTP(
    endpoint=data['data']['endpoint'], 
    api_key=data['data']['api'],
    api_secret=data['data']['secret']
)

drawdown = 5

while True:
    positions = session.my_position()
    for p in positions['result']:
        if float(p['data']['size']) > 0 or float(p['data']['size']) < 0:
            #(4006.33-7.32)*40468/4006.33*0.099
            value = ( float(p['data']['position_value']) + float(p['data']['unrealised_pnl']) ) * float(p['data']['entry_price']) / float(p['data']['position_value']) * float(p['data']['size'])
            #Retrieve current position value based on current Profit.

            #get Unrealized P%L considering leverage as well.
            #This is faster than ByBit frontend, so you will may experience some small differences.
            pl = (value-float(p['data']['position_value'])) / float(p['data']['position_value']) * 100 * float(p['data']['leverage'])

            if pl < drawdown*-1:
                print('Close position')
                if p['data']['side'] == 'Buy':
                    session.place_active_order(
                        side="Sell",
                        symbol=p['data']['symbol'], 
                        order_type="Market", 
                        qty=p['data']['size'], 
                        time_in_force="FillOrKill", 
                        reduce_only=True, 
                        close_on_trigger=True
                    )
                else:
                    session.place_active_order(
                        side="Buy",
                        symbol=p['data']['symbol'],
                        order_type="Market",
                        qty=p['data']['size'],
                        time_in_force="FillOrKill", 
                        reduce_only=True, 
                        close_on_trigger=True
                    )
    time.sleep(1)


