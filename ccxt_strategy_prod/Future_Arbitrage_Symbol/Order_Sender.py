from Demo_apikey_oop import ExchangeAPI
from Demo_insert_csv import OperationCSV

class TradingBot:
    def __init__(self, root_path, api_key_file, exchange_name, leverage, symbol, trade_type, text):
        self.root_path = root_path
        self.api_key_file = api_key_file
        self.exchange_name = exchange_name
        self.leverage = leverage
        self.symbol = symbol
        self.trade_type = trade_type
        self.text = text
        
        # Initialize ExchangeAPI
        self.exchange_api = ExchangeAPI(root_path, api_key_file, exchange_name, leverage, symbol, trade_type)
        self.exchange_api.set_leverage(leverage, symbol)
        
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

    def _record_order(self, order, price, side, amount):
        record_root_path = self.root_path
        record_filename = "Z_Strategy_arbitrage_info.csv"
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

    def _record_close_position(self, profit, fees, close_price, close_amount, direction, close_time):
        record_root_path = self.root_path
        record_filename = "Z_Strategy_arbitrage_info.csv"
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
    
    def send_order_open(self, order_type, order_side, amount, price):
        order = self.exchange_api.create_order(self.symbol, order_type, order_side, amount, price, self.text)
        self._record_order(order, price, order_side, amount)
        return order

    def send_order_close(self,price,amount):
        order = self.close_position(price, amount,self.text)
        print("---------- debug 5")
        return order   

