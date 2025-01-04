# Demo_apikey_oop.py

import json
import ccxt
import pandas as pd

class ExchangeAPI:
    def __init__(self, root_path, api_key_file, exchange_name,leverage,symbol,trade_type):
        self.root_path = root_path
        self.api_key_file = api_key_file
        self.exchange_name = exchange_name
        self.leverage = leverage
        self.symbol = symbol
        self.trade_type = trade_type
        self.filepath = f"{self.root_path}/{self.api_key_file}"
        self.api_key_info = self.read_api_key()
        self.apiKey = self.api_key_info['apiKey']
        self.secret = self.api_key_info['secret']
        self.exchange = self.init_exchange()
        
    def init_exchange(self):
        try:
            exchange_class = getattr(ccxt, self.exchange_name)
            exchange = exchange_class({
                'apiKey': self.apiKey,
                'secret': self.secret,
                'options': {
                    'defaultType': self.trade_type,  # 如果使用的是现货交易，更改为 'spot'
                },
            })
            #print(f"Initialized exchange: {exchange}")  # Debug: 确认 exchange 实例初始化正确
            return exchange
        except AttributeError:
            raise ValueError(f"Exchange '{self.exchange_name}' not found in ccxt library.")
        except Exception as e:
            raise RuntimeError(f"Error initializing exchange: {e}")

    def fetch_ohlcv(self, symbol, timeframe, limit):
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit) 
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            raise RuntimeError(f"Error fetching OHLCV data: {e}")
        
    def read_api_key(self):
        with open(self.filepath, 'r') as file:
            api_key_info = json.load(file)
        return api_key_info

    def set_leverage(self, leverage, symbol):
        try:
            print(f"Setting leverage on exchange: {self.exchange.id}, Symbol: {symbol}, Leverage: {leverage}")
            return self.exchange.set_leverage(leverage, symbol)
        except Exception as e:
            raise RuntimeError(f"Error setting leverage: {e}")
        
    def get_api_key_info(self):
        return self.api_key_info

    def get_exchange(self):
        return self.exchange
    

    def fetchMyTrades(self):
        return  self.exchange.fetchMyTrades();

    def fetch_balance(self):
        try:
            balance = self.exchange.fetch_balance()
            balance_info = balance['info']

            balance = self.exchange.fetch_balance(params={"type": "spot"})

            # 提取 USDT 余额
            usdt_balance = balance['total'].get('USDT', 0)
            return usdt_balance
        except Exception as e:
            raise RuntimeError(f"Error fetching balance: {e}")
    
    # 获取现货账户资产估值
    def get_total_asset_value(self):
        try:
            # 获取账户余额
            balance = self.exchange.fetch_balance(params={"type": "spot"})
            total_asset_value = 0.0

            # 遍历所有资产
            for asset, details in balance['total'].items():
                if details > 0:  # 如果余额大于0
                    if asset == 'USDT':  # 如果是USDT，直接计入总资产
                        total_asset_value += details
                    else:
                        # 获取资产对USDT的当前价格
                        symbol = f"{asset}/USDT"
                        try:
                            ticker = self.exchange.fetch_ticker(symbol)
                            price = ticker['last']  # 获取最新价格
                            total_asset_value += details * price  # 计算该资产的估值
                        except Exception as e:
                            print(f"无法获取 {symbol} 的价格: {e}")

            print(f"账户总资产估值（USDT）: {total_asset_value:.2f}")
            return total_asset_value

        except Exception as e:
            print(f"发生错误: {e}")
            return None

    def fetch_recent_trades(self, symbol, limit=10):
        try:
            trades = self.exchange.fetch_my_trades(symbol, limit=limit)
            #print("trades--------")
            #print(trades)
            #print("trades--------")
            fee = 0;
            for order in trades:
                order_id = order['info']['order_id']
                order_fee = round(float(order['info']['fee']),4)
                order_fee_total = fee + order_fee
                order_text = order['info']['text']
                order_symbol = order['info']['contract']
                order_size = order['info']['size']
                
                print("order_id: ",order_id,"   order_fee_total: ",order_fee_total," order_text: ",order_text,"  order_symbol: ",order_symbol, order_size)     
            return trades
        
        except Exception as e:
            raise RuntimeError(f"Error fetching recent trades: {e}")
        
    def fetch_close_price(self, symbol):
        try:
            price = self.exchange.fetch_ticker(symbol)['last']
            return price
        except Exception as e:
            raise RuntimeError(f"Error fetching close price: {e}")

    def fetch_order_book(self, symbol):
        try:
            orderbook = self.exchange.fetch_order_book(symbol)
            bid = orderbook['bids'][0][0] if orderbook['bids'] else None
            ask = orderbook['asks'][0][0] if orderbook['asks'] else None
            spread = (ask - bid) if (bid and ask) else None
            return bid, ask, spread
        except Exception as e:
            raise RuntimeError(f"Error fetching order book: {e}")

    def create_order(self, symbol, order_type, side, amount, price, text):
        try:
            params = {}
            if text:
                params['text'] = text  # 添加自定义文本字段
            market = self.exchange.market(symbol)
            min_amount = market['limits']['amount']['min']
            max_amount = market['limits']['amount']['max']
            if amount < min_amount:
                raise ValueError(f"Amount {amount} is less than the minimum amount {min_amount}")
            if(side=="buy"):
                params = {'newOrderRespType': 'RESULT'}
                order = self.exchange.create_order(symbol, order_type, side, amount, price, params)  
            else:
                order = self.exchange.create_market_sell_order(symbol, amount)    
            return order
        except Exception as e:
            raise RuntimeError(f"Error creating order: {e}")

    def fetch_open_orders(self, symbol):
        try:
            orders = self.exchange.fetch_open_orders() #– 获取未完成订单的列表。
            print("fetch_open_orders:  ",orders)
            return orders
        except Exception as e:
            raise RuntimeError(f"Error fetching open orders: {e}")
        
    def fetch_positions(self, symbol):
        positions = self.exchange.fetch_positions()
        profit = 0;
        fees = 0;
        profit_total = 0;
        initialMargin = 0;
        entryPrice = 0;
        direction = '';
        leverage = 0;
        for position in positions:
            Contract = position['symbol']
            print('onPositions: ----------------------')
            print(position)
            print('----------------------')
            #print(Contract)
            if Contract== symbol:
                '''
                print("-------------------")
                print("浮动盈亏:  "+str(position['unrealizedPnl']))
                print("手续费:  "+str(position['realizedPnl']))
                print("总盈亏: "+str(position['unrealizedPnl']+position['realizedPnl']))
                
                #账户基本信息
                balance = self.exchange.fetch_balance();
                print("Balance Total: ",balance['USDT']['total']);
                print("Balance Free: ",balance['USDT']['free']);

                print("-------------------")
                #margin -> 保证金
                print("initialMargin")
                print(self.exchange.fetch_position(symbol)['initialMargin']) 

                print("-------------------")
                #margin 
                #print("marginBalance")
                #print(exchange_swap.fetch_position(symbol)['marginBalance']) 

                print("-------------------")
                #交易入场价格
                print("交易入场价格")
                print(self.exchange.fetch_position(symbol)['entryPrice']) 

                print("-------------------")
                #交易数量
                print("交易数量")
                print(self.exchange.fetch_position(symbol)['contracts'] )

                print("-------------------")
                #交易方向
                print("交易方向")
                print(self.exchange.fetch_position(symbol)['side'] )

                print("-------------------")
                #交易杠杆
                print("交易杠杆")
                print(self.exchange.fetch_position(symbol)['leverage'] )
                '''
                profit = round(float(position['unrealizedPnl']), 4);
                fees = round(float(position['realizedPnl']), 4);
                profit_total = round(float(position['unrealizedPnl']+position['realizedPnl']), 4);
                initialMargin = round(float(position['initialMargin']), 4);
                entryPrice = round(float(position['entryPrice']), 4);
                amounts  = position['contracts'];
                direction = str(position['side']);
                leverage =  position['leverage'];
                break;
        return profit, fees,  profit_total,initialMargin,entryPrice,amounts,direction,leverage
    
    def close_position(self, symbol,price, amount,text):
        print("------ test 1")
        try:
            # 获取当前持仓信息
            position = self.exchange.fetch_position(symbol)
            direction = position['side']

            print("position----------------")
            print(position)
            print("----------------")
            print("Amount: "+ str(float(position['contracts'])))
            # 如果有持仓，则进行平仓操作
            if position['contracts'] > 0:
                # 计算平仓数量，假设平掉全部持仓
                #amount_to_close = position['contracts']

                profit = round(float(position['unrealizedPnl']), 4);
                fees = round(float(position['realizedPnl']), 4);

                # 下平仓市价卖单
                order = []
                print("-------symbol: ",symbol,"   amount: ",amount,"  price: ",price,"   text: ",text)
                if direction == 'short':
                    order = self.create_order(symbol, 'market', 'buy', amount, price,text)
                else:
                    order = self.create_order(symbol, 'market', 'sell', amount, price,text)
                
                print("平仓订单已下单：", order)

                # 计算已实现盈利和手续费
                close_price = order['price']
                close_time  = order['datetime']
                close_amount = order['amount']
                close_direction = order['side']
                
                # 获取订单编号
                order_id = order['id']

                
                print("订单编号：", order_id)           
                print("当前总实现盈利：", profit)
                print("当前总手续费：", fees)
                print("平仓价格：", close_price)
                print("平仓时间：", close_time)
                print("平仓数量：", close_amount)
                

                print("---------- debug 4")
                return order_id,profit,fees,close_price,close_amount,close_direction,close_time
            else:
                print("当前无持仓，无需平仓")
                return None


        except Exception as e:
            raise RuntimeError(f"！！！！ Error closing position: {e}")

    # 获取订单信息
    def get_order_info(self,order_id, symbol):
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return order
        except ccxt.BaseError as e:
            print("获取订单信息时出错:", str(e))
            return None                                                                     

    def fetch_Closed_Orders(self):
        fco = self.exchange.fetchClosedOrders()
        return fco

    def close_position_by_order(self,order_id, symbol):
        order = self.exchange.fetch_order(order_id, symbol)

        if order:
            print("订单信息:", order)
            # 检查订单是否已完全成交
            if order['status'] != 'closed':
                print("订单未完全成交，无法平仓")
                return

            # 获取持仓信息
            position = self.exchange.get_position(symbol)
            if position:
                try:
                    # 获取当前仓位数量
                    position_amt = float(position['positionAmt'])
                    if position_amt == 0:
                        print("没有仓位需要平仓")
                        return

                    # 平仓订单方向
                    order_side = 'sell' if position_amt > 0 else 'buy'
                    abs_position_amt = abs(position_amt)

                    # 创建平仓订单
                    order = self.exchange.create_order(
                        symbol=symbol,
                        type='market',
                        side=order_side,
                        amount=abs_position_amt
                    )
                    print("平仓订单已创建:", order)
                except ccxt.BaseError as e:
                    print("平仓时出错:", str(e))
            else:
                print("未找到该交易对的持仓信息")
        else:
            print("未找到订单信息")


                