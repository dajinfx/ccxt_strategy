from Demo_apikey_oop import ExchangeAPI
from Demo_insert_csv import OperationCSV
from datetime import datetime
from Logger import Logger
import ccxt

class TradingBot:
    def __init__(self, root_path, api_key_file, exchange_name, leverage, symbol, trade_type, text,db,logPath):
        self.root_path = root_path
        self.api_key_file = api_key_file
        self.exchange_name = exchange_name
        self.leverage = leverage
        self.symbol = symbol
        self.trade_type = trade_type
        self.text = text
        self.db  = db 
        self.logPath = logPath
        
        # Initialize ExchangeAPI
        self.exchange_api = ExchangeAPI(root_path, api_key_file, exchange_name, leverage, symbol, trade_type)
        #self.exchange_api.set_leverage(leverage, symbol)
        
    def get_balance_info(self):
        
        balance, balance_info, balance_used, balance_unrealized, fee = self.exchange_api.fetch_recent_trades(self.symbol, limit=10)
        return balance, balance_info, balance_used, balance_unrealized, fee

    def get_market_info(self):
        price = self.exchange_api.fetch_close_price(self.symbol)
        bid, ask, spread = self.exchange_api.fetch_order_book(self.symbol)
        return price,bid, ask, spread

    def get_position_info(self):
        profit, fees, profit_total, initialMargin, entryPrice, amounts, entrydirection, leverage = self.exchange_api.fetch_positions(self.symbol)
        return profit, fees, profit_total, initialMargin, entryPrice, amounts, entrydirection, leverage

    def close_orders(self):
        self.exchange_api.close_position(self.symbol)

    def _record_order_csv(self, order, price, side, amount):
        record_root_path = self.root_path
        record_filename = self.record_filename 
        operate_csv = OperationCSV(record_root_path, record_filename)
        
        colvalue = [
            self.text,
            self.exchange_name,
            str(order['id']),
            self.symbol,
            price,
            side,
            amount,
            order['datetime'],
            'open'
        ]
        operate_csv.add_row_if_empty(colvalue)

        colvalue.clear();
    
   
    def _record_order_db(self,exchange_name, symbol, order_type, order_id, price, side, amount,formatted_time, trade_id,open_close):
        
        if open_close == 'open':
            query = "insert into strategy_binance (str_order_id, str_platform, str_market, str_symbol_1, str_symbol_2, \
                                    str_open_price, str_open_direction, str_open_size, str_open_time)\
                                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            
            pair = symbol
            base, quote = pair.split("/")
            values = [(
                order_id,
                exchange_name,
                order_type,
                base,
                quote,
                price,
                side,
                amount,
                formatted_time 
                )
            ]
        else:
            query = "update strategy_binance set str_status = 'close', str_close_price = %s,str_close_direction=%s,str_close_size=%s where str_order_id = %s;"
            values = [(price,side,amount,trade_id)]

        print("query:  ",query)
        logger_msg = Logger(self.logPath)
        msg_value = "order_id: "+order_id+"   price: "+str(price)+"  side: "+side+"  amount: "+str(amount)+"   formatted_time: "+formatted_time+"  trade_id: "+trade_id;
        message = "query:  "+query+"\n"+msg_value
        logger_msg.write_log(message)
        self.db.insert_into(query,values)

    def close_position(self,price, amount, text):
        print("debug - 1")
        try:
            result = self.exchange_api.close_position(self.symbol, price, amount,text)
            if result:
                order_id,profit, fees, close_price, close_amount, direction, close_time = result
                self._record_close_position(profit, fees, close_price, close_amount, direction, close_time)
                print("Position closed successfully!")
            else:
                print("No position to close or position size is zero.")
        except Exception as e:
            print(f"Error closing position: {e}")

    def _record_close_position_csv(self, profit, fees, close_price, close_amount, direction, close_time):
        record_root_path = self.root_path
        record_filename = self.record_filename 
        operate_csv = OperationCSV(record_root_path, record_filename)

        colvalue = [
            'closed',
            profit,
            fees,
            profit + fees,
            close_price,
            close_amount,
            direction,
            close_time
        ]
        operate_csv.update_csv_rows(self.text, colvalue)
        colvalue.clear();
    
    def send_order_open(self, order_type, order_side, amount, price, trade_id,open_close):
        try:
            order = self.exchange_api.create_order(self.symbol, order_type, order_side, amount, price, self.text)
            #self._record_order(order, price, order_side, amount)
            now = datetime.now()

            # 格式化时间为 YYYYmmdd:hhss 格式
            formatted_time = now.strftime("%Y%m%d:%H%M%S")
            print(formatted_time)
            print(order)

            order_id = now.strftime("%Y%m%d%H%M%S")
            self._record_order_db(self.exchange_name, self.symbol,order_type, order_id,price, order_side, amount,formatted_time, trade_id,open_close)
            
            logger_msg = Logger(self.logPath)
            message = "order success "
            logger_msg.write_log(message)

            print("formatted_time: ", formatted_time,"  now:  ",now,"    order_id:  ",order_id)
        except ccxt.BaseError as e:
            print("成交订单时出错:", str(e))
            logger_msg = Logger(self.logPath)
            message = "Error msg:  "+str(e)
            logger_msg.write_log(message)
            return None  

        return True

    def send_order_close(self,price,amount):
        order = self.close_position(price, amount,self.text)
        return order   

