import ccxt
import talib
import pandas as pd
import schedule
import time
from Order_Sender import TradingBot
from Demo_apikey_oop import ExchangeAPI
from Demo_insert_csv import OperationCSV
import datetime

class Scalping_1:
    def __init__(self, bot_1,bot_2,api_1,api_2,symbol_1,symbol_2, price_gap, order_trigger, order_size,order_profit,order_canbuy_1,order_cansell_1,text,root_path,record_filename):
        self.bot_1 = bot_1
        self.bot_2 = bot_2
        self.api_1 = api_1
        self.api_2 = api_2
        
        self.text = text
        self.root_path = root_path
        self.record_filename = record_filename
        self.symbol_1 = symbol_1
        self.symbol_2 = symbol_2
        self.size = order_size
        self.price_gap = price_gap
        self.order_trigger = order_trigger
        self.profit = order_profit
        self.order_canbuy_1 = order_canbuy_1
        self.order_cansell_1 = order_cansell_1

    def calculate_rsi(self, df, period=14):
        df['rsi'] = talib.RSI(df['close'], timeperiod=period)
        return df

    def check_buy_1_signal(self):
        price_1, bid_1, ask_1, spread_1 = self.bot_1.get_market_info()
        price_2, bid_2, ask_2, spread_2 = self.bot_2.get_market_info()

        ask_1 = ask_1+self.price_gap
        if (ask_2 - ask_1) > self.order_trigger:
                return;

        return False
    
    def check_sell_1_signal(self, df, rsi_threshold=55):
        print("sellSignal:  ",df['rsi'].iloc[-1])
        if df['rsi'].iloc[-1] > rsi_threshold:
            if self.order_cansell ==1:
                return True
        return False

    def execute_strategy(self):
        print('execute_strategy start')
        openCsv = OperationCSV(self.root_path,self.record_filename)
        csvRows = openCsv.check_open_order(self.text)
        print(csvRows)
        print(len(csvRows))
        
        buy_signal = self.check_buy_1_signal()
        sell_signal = self.check_sell_1_signal()

        if len(csvRows)==0:
            print('1----')
            if buy_signal:
                print(f"{pd.Timestamp.now()} - Buy signal! RSI is below 25.")
                price, bid, ask, spread = self.bot.get_market_info()
                self.bot.send_order_open('market', 'buy', self.size, ask)
            if sell_signal:
                print(f"{pd.Timestamp.now()} - sell signal! RSI is upper 75.")
                price, bid, ask, spread = self.bot.get_market_info()
                self.bot.send_order_open('market', 'sell', self.size, bid)
        else:
            if csvRows[0][5] == 'buy':
                if sell_signal:
                    profit, fees, profit_total, initialMargin, entryPrice, amounts, entrydirection, leverage = self.bot.get_position_info()
                    price, bid, ask, spread = self.bot.get_market_info()
                    if profit_total > self.profit:
                        self.bot.send_order_close(bid,self.size)  
                        print(f"{pd.Timestamp.now()} - Closing position with profit: {profit_total} USDT")
            elif csvRows[0][5] == 'sell':
                if buy_signal:
                    profit, fees, profit_total, initialMargin, entryPrice, amounts, entrydirection, leverage = self.bot.get_position_info()
                    price, bid, ask, spread = self.bot.get_market_info()
                    if profit_total > self.profit:
                        self.bot.send_order_close(ask,self.size)  
                        print(f"{pd.Timestamp.now()} - Closing position with profit: {profit_total} USDT")

        now = datetime.datetime.now()
        formatted_now = now.strftime("%Y/%m/%d %H:%M:%S")                
        print('execute_strategy End: ',formatted_now)
        
if __name__ == "__main__":
    # Configuration
    exchange_name = 'gateio'
    root_path = "D:/交易/ccxtdoc"
    api_key_file = "Gate_io/APIKey.txt"
    leverage = 5

    symbol_1 = 'ETHW/USDT:USDT'
    symbol_2 = 'ETHFI/USDT:USDT' 
    trade_type = 'swap'
    text = "dajin_arbitrage_ETHW_ETHFI"
    record_filename = "Z_Strategy_arbitrage_ETHW_ETHFI.csv"

    order_size = 1;
    order_profit = 0.1;
    order_canbuy_1 = 1;
    order_cansell_1 = 0;

    api_1 = ExchangeAPI(root_path, api_key_file, exchange_name, leverage, symbol_1, trade_type)
    api_2 = ExchangeAPI(root_path, api_key_file, exchange_name, leverage, symbol_2, trade_type)

    # Initialize TradingBot
    bot_1 = TradingBot(root_path, api_key_file, exchange_name, leverage, symbol_1, trade_type, text)
    bot_2 = TradingBot(root_path, api_key_file, exchange_name, leverage, symbol_2, trade_type, text)
    
    # Initialize Scalping_1 Strategy
    scalping_strategy = Scalping_1(bot_1,bot_2,api_1,api_2,symbol_1,symbol_2,order_size,order_profit,order_canbuy_1,order_cansell_1 ,text,root_path,record_filename)

    # Schedule the strategy to run every minute
    schedule.every(300).seconds.do(scalping_strategy.execute_strategy)
    
    while True:
        schedule.run_pending()
        time.sleep(10)












