import ccxt
import pandas as pd
import time
from Order_Sender import TradingBot
from Demo_apikey_oop import ExchangeAPI
from Demo_insert_csv import OperationCSV
from ta.momentum import RSIIndicator
import datetime
import schedule
from Order_db_connection import Order_db_connection 
from Logger import Logger
import json
import os

class Scalping_1:
    def __init__(self, bot_1,api_1,symbol_1,symbol_2, order_size,order_profit,order_canbuy_1,order_cansell_1,text,root_path,db,logPath):
        self.bot_1 = bot_1
        self.api_1 = api_1
        
        self.text = text
        self.root_path = root_path
        self.symbol_1 = symbol_1
        self.symbol_2 = symbol_2
        self.symbol   = symbol_1 + "/" + symbol_2
        self.size = order_size
        self.profit = order_profit
        self.order_canbuy_1 = order_canbuy_1
        self.order_cansell_1 = order_cansell_1
        self.db = db
        self.logPath = logPath

    def check_buy_1_signal(self,df, rsi_threshold=14):
        price_1, bid_1, ask_1, spred = self.bot_1.get_market_info()
        print("price: ",price_1);
        print("bid_1: ",bid_1);
        print("ask_1: ",ask_1);

        rsi = RSIIndicator(close=df['close'], window=rsi_threshold)
        # 获取 RSI 的完整序列
        rsi_series = rsi.rsi()
        df['rsi'] = rsi.rsi()
        

        if(rsi_series.iloc[-1]<50):
            print("buy signal true")
            
            logger_msg = Logger(self.logPath)
            message = "buySignal:  ",df['rsi'].iloc[-1]
            logger_msg.write_log(message)
            print("rsi:  ",rsi_series.iloc[-1])

            return False;
        return False
    
    def check_sell_1_signal(self, df, rsi_threshold=14):
        rsi = RSIIndicator(close=df['close'], window=rsi_threshold)
        # 获取 RSI 的完整序列
        rsi_series = rsi.rsi()
        df['rsi'] = rsi.rsi()

        # 最后一个K线 rsi的 值
        print("rsi:  ",rsi_series.iloc[-1])

        if(rsi_series.iloc[-1]>65):
            print("sell signal true")
            return True;
        return True

    def check_balance(self):
        balance = self.api_1.fetch_balance()

        total_asset = api_1.get_total_asset_value()
        print("balance: ",balance)
        print("total_asset: ",total_asset)

    def execute_strategy(self):
        logger_msg = Logger(self.logPath)
        message = "------------"
        print("self.logPath: ",self.logPath,"   message: ",message)
        logger_msg.write_log(message)

        print('execute_strategy start')
        #openCsv = OperationCSV(self.root_path,self.record_filename)

        Quary = "SELECT * FROM Strategy_binance where str_open_direction = 'buy' and (str_status is null or str_status = '')  order by str_open_price asc LIMIT 1;";  #判断有没有 buy 的开仓，但没有平仓
        result = self.db.query_into(Quary)
        trade_side = '';
        trade_id   = '';
        trade_size   = 0;
        trade_price  = 0;
        for row in result:
            trade_side = row[7]
            trade_id   = row[1]
            trade_size = row[8]
            trade_price = row[6]
            break;
        
        df = self.api_1.fetch_ohlcv(self.symbol,timeframe, limit );

        #得到指标值
        buy_signal = self.check_buy_1_signal(df)
        sell_signal = self.check_sell_1_signal(df)
        

        if buy_signal:
            print(f"{pd.Timestamp.now()} - Buy signal! RSI is below 25.")
            price, bid, ask, spread = self.bot_1.get_market_info()
            order = self.bot_1.send_order_open('market', 'buy', self.size, ask,trade_id,'open') 

            message = "buy open"
            logger_msg.write_log(message)

        '''
        if sell_signal:
            print(f"{pd.Timestamp.now()} - sell signal! RSI is upper 75.")
            price, bid, ask, spread = self.bot_1.get_market_info()
            order = self.bot_1.send_order_open('market', 'sell', self.size, bid,'open')
        '''
         
        if len(result)>0: #如果没有 空仓，或者已经都平仓
            print("opened trade_side: ",trade_side)
            print("sell_signal: ",sell_signal)
            print("buy_signal:  ",buy_signal)
            if trade_side == 'buy':  #已开仓方向
                if sell_signal:      #平仓方向
                    print('go to sell')
                    #profit, fees, profit_total, initialMargin, entryPrice, amounts, entrydirection, leverage = self.bot_1.get_position_info()
                    price, bid, ask, spread = self.bot_1.get_market_info()

                    if bid > trade_price:
                        #if profit_total > self.profit:
                        order = self.bot_1.send_order_open('market', 'sell', self.size, bid, trade_id,'close')
                        
                        message = "buy close"
                        logger_msg.write_log(message)

                    else:
                        print('price is low, can not trade.')

            elif trade_side == 'sell': #已开仓方向
                if buy_signal:         #平仓方向
                    print('go to buy')
                    ##profit, fees, profit_total, initialMargin, entryPrice, amounts, entrydirection, leverage = self.bot_1.get_position_info()
                    price, bid, ask, spread = self.bot_1.get_market_info()
                    order = self.bot_1.send_order_open('market', 'buy', self.size, ask, trade_id,'close') 
                                
                    message = "sell close"
                    logger_msg.write_log(message)

        now = datetime.datetime.now()
        formatted_now = now.strftime("%Y/%m/%d %H:%M:%S")                
        print('execute_strategy End: ',formatted_now)

def read_dbinfo(dbInfo_filepath):
    with open(dbInfo_filepath, 'r') as file:
        db_info = json.load(file)
        host = db_info ['host']
        user = db_info ['user']
        password = db_info ['password']
        database = db_info ['database']
        auth_plugin = db_info ['auth_plugin']
    return host,user,password,database,auth_plugin

if __name__ == "__main__":
    # Configuration
    exchange_name = 'binance'
    root_path = "D:/TradeData/ccxtdoc"
    api_key_file = "Binance/APIKey.txt"
    leverage = 1
    
    current_folder_path = os.path.dirname(os.path.abspath(__file__))
    logPath = current_folder_path + '/LogBinance/log_scalping_DOGE.txt'

    symbol_1 = 'DOGE'
    symbol_2 = 'USDT'
    symbol = symbol_1 + "/" + symbol_2
    trade_type = 'spot'
    text = "dajin_DOGE_RSI_Buy"

    order_size = 10;
    order_profit = 0.1;
    order_canbuy_1 = 1;
    order_cansell_1 = 0;
    timeframe = '5m';
    limit =50;
    
    dbInfo_filepath = root_path+"/DBInfo/db_info.txt"  
    host, user,password,database,auth_plugin = read_dbinfo(dbInfo_filepath)
    db = Order_db_connection(host,user,password,database,auth_plugin)

    # Initialize Get API
    api_1 = ExchangeAPI(root_path, api_key_file, exchange_name, leverage, symbol, trade_type)
    # Initialize TradingBot
    bot_1 = TradingBot(root_path, api_key_file, exchange_name, leverage, symbol, trade_type, text,db,logPath)
    
    
    # Initialize Scalping_1 Strategy
    scalping_strategy = Scalping_1(bot_1,api_1,symbol_1,symbol_2,order_size,order_profit,order_canbuy_1,order_cansell_1 ,text,root_path,db,logPath)
        # Schedule the strategy to run every minute

    scalping_strategy.check_balance()  
    scalping_strategy.execute_strategy() 
    ''' 
    schedule.every(30).seconds.do(scalping_strategy.execute_strategy)
    
    while True:
        schedule.run_pending()
        #time.sleep(10)
    '''

    

    












