import time
import json
import pprint
from pybit import usdt_perpetual
import os
from colorama import Fore, Style

def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

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
    clearConsole()
    print(f'{Fore.WHITE}Open positions:')
    for p in positions['result']:
        try:
            if float(p['data']['size']) > 0 or float(p['data']['size']) < 0:
                #(4006.33-7.32)*40468/4006.33*0.099
                value = ( float(p['data']['position_value']) + float(p['data']['unrealised_pnl']) ) * float(p['data']['entry_price']) / float(p['data']['position_value']) * float(p['data']['size'])
                #Retrieve current position value based on current Profit.

                #get Unrealized P%L excluding leverage
                #This is faster than ByBit frontend, so you will may experience some small differences.
                pl = (value-float(p['data']['position_value'])) / float(p['data']['position_value']) * 100
                
                if float(p['data']['unrealised_pnl']) > 0:
                    if p['data']['side'] == 'Buy':
                        print(f"{Fore.BLUE}{p['data']['symbol']}    {Fore.GREEN}BUY     {Fore.WHITE}DD: {Fore.GREEN}{round(pl,2)}%    {Fore.WHITE}Profit: {Fore.GREEN}{p['data']['unrealised_pnl']}")
                    else:
                        print(f"{Fore.BLUE}{p['data']['symbol']}    {Fore.RED}SELL    {Fore.WHITE}DD: {Fore.GREEN}{round(pl,2)}%    {Fore.WHITE}Profit: {Fore.GREEN}{p['data']['unrealised_pnl']}")
                else:
                    if p['data']['side'] == 'Buy':
                        print(f"{Fore.BLUE}{p['data']['symbol']}    {Fore.GREEN}BUY     {Fore.WHITE}DD: {Fore.RED}{round(pl,2)}%    {Fore.WHITE}Profit: {Fore.RED}{p['data']['unrealised_pnl']}")
                    else:
                        print(f"{Fore.BLUE}{p['data']['symbol']}    {Fore.RED}SELL    {Fore.WHITE}DD: {Fore.RED}{round(pl,2)}%    {Fore.WHITE}Profit: {Fore.RED}{p['data']['unrealised_pnl']}")
                
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
        except Exception as e:
            print(f'Something went wrong {e}')
    time.sleep(1)


