import ccxt
import talib
import pandas as pd
import schedule
import time
from Order_Sender import TradingBot
from Demo_apikey_oop import ExchangeAPI
from Demo_insert_csv import OperationCSV

if __name__ == "__main__":
    # Configuration
    exchange_name = 'gateio'
    root_path = "D:/交易/ccxtdoc"
    api_key_file = "Gate_io/APIKey.txt"
    leverage = 5
    symbol = 'LTC/USDT:USDT'
    trade_type = 'swap'
    text = "dajin_arbitrade_spot_future"
    record_filename = "Z_Strategy_arbitrage_info.csv"

    api = ExchangeAPI(root_path, api_key_file, exchange_name, leverage, symbol, trade_type)

    # Initialize TradingBot
    bot = TradingBot(root_path, api_key_file, exchange_name, leverage, symbol, trade_type, text)
    
    #def send_order_open(self, order_type, order_side, amount, price):  order_type->'market'/'limit'

    price, bid, ask, spread = bot.get_market_info()

    print(price, bid, ask, spread)
    #bot.send_order_open('market','buy', 1, ask)

    #bot.send_order_close(ask,1)
    
    openCsv = OperationCSV(root_path,record_filename)
    rows = openCsv.check_open_order(text)


    api.fetch_ohlcv(symbol,'1m',100)


    #print(api.fetch_ohlcv(symbol,'1m',100))
    print(bot.get_market_info())


