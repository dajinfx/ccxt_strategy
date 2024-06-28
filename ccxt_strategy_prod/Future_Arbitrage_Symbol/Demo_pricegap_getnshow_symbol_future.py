import ccxt
from datetime import datetime
import time

import csv
import json
# Libraries to help with reading and manipulating data
import numpy as np
import pandas as pd
# Libraries to help with data visualization
import matplotlib.pyplot as plt
import seaborn as sns

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')

symbol_main_1 = "ETHW";
root_path = "D:/TradeData"
symbol_pair = "USDT:USDT";
symbol_1 = symbol_main_1 + '/'+ symbol_pair;
symbol_future_1 = symbol_1

symbol_main_2 = "ETHFI";
symbol_2 = symbol_main_2 + '/'+ symbol_pair;
symbol_future_2 = symbol_2

symbol_pricegab = 0.8;
filename = root_path + '/ccxt_data_symbol_'+symbol_main_1+'_'+symbol_main_2+'.csv'

#Write down to csv
def write_info_to_csv(data, filename):
    print("------------------------------------------------------")
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['timeStamp', 'FuturePrice_1_1','FuturePrice_1_2','FuturePrice_1_3', 'FuturePrice_2_1','FuturePrice_2_2','FuturePrice_2_3', 'timeRegular'])
        writer.writeheader()
        for item in data:
            print(item);
            writer.writerow(item)
    print("------------------------------------------------------")


exchange = ccxt.gateio({'options': {'defaultType': 'swap'}})

timeframe = '5m'
limit = 1000
ohlcv_future_1 = exchange.fetch_ohlcv(symbol_future_1, timeframe, limit=limit)

def PriceMerge(data_spot, data_futures):
    processed_data = [];
    
    i = 0;
    for candle1 in data_spot:
        timeStamp = candle1[0]
        # Convert timestamp to seconds
        timeStampSeconds = timeStamp / 1000
        # Convert to local time
        timeArray = time.localtime(timeStampSeconds)
        # Format the time
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        # Create a dictionary for the row
        row = {
            'timeStamp': candle1[0],
            'FuturePrice_1_1': candle1[1]+symbol_pricegab,
            'FuturePrice_1_2': candle1[2]+symbol_pricegab,
            'FuturePrice_1_3': candle1[3]+symbol_pricegab,
            'FuturePrice_2_1': data_futures[i][1],
            'FuturePrice_2_2': data_futures[i][2],
            'FuturePrice_2_3': data_futures[i][3],
            'timeRegular': otherStyleTime
        }
        processed_data.append(row)
        i=i+1;
        print(row)
    write_info_to_csv(processed_data, filename);
    

print("------------------------------------------------------")
#outputPrice( "Spot", ohlcv_spot);
print("------------------------------------------------------")


binance_futures = ccxt.binance({'options': {'defaultType': 'swap'}})

ohlcv_future_2 = binance_futures.fetch_ohlcv(symbol_future_2, timeframe, limit=limit)

print("------------------------------------------------------")
#outputPrice( "Future", ohlcv_future);
print(ohlcv_future_2)

PriceMerge(ohlcv_future_1, ohlcv_future_2)

# 读取 CSV 文件
try:
    data = pd.read_csv(filename)
    print(f"成功读取文件: {filename}")
except FileNotFoundError:
    print(f"文件未找到: {filename}")
    data = None

# 显示数据的一些信息
if data is not None:
    print("数据预览:")
    print(data.head())
else:
    print("无法显示数据，因为文件未找到或读取失败。")

data.head()
df = pd.DataFrame(data)


# 假设 df 已经存在，并且包含 'timeRegular', 'FuturePrice_1_1', 'FuturePrice_2_1' 三列
df['timeRegular'] = pd.to_datetime(df['timeRegular'])

# 计算两个数据集之间的差异
df['Difference'] = (df['FuturePrice_1_1'] - df['FuturePrice_2_1']).abs()

# 找到前五个最大差异
top_differences = df.nlargest(5, 'Difference')

# 绘制现货和期货的收盘价格线图
plt.figure(figsize=(14, 7))
plt.plot(df['timeRegular'], df['FuturePrice_1_1'], label='Gateio_1', marker='o', linewidth=2, alpha=0.8, markersize=4)
plt.plot(df['timeRegular'], df['FuturePrice_2_1'], label='Gateio_1', marker='o', linewidth=2, alpha=0.8, markersize=4)

# 标注前五个最大差异的位置
for i, row in top_differences.iterrows():
    max_diff_time = row['timeRegular']
    max_diff_value_1 = row['FuturePrice_1_1']
    max_diff_value_2 = row['FuturePrice_2_1']
    max_diff = row['Difference']
        # 打印最大差异的信息
    print("max_diff_time: " + str(max_diff_time))
    print("max_diff_value_1: " + str(max_diff_value_1))
    print("max_diff_value_2: " + str(max_diff_value_2))
    print("max_diff: " + str(max_diff))
        
    plt.annotate(f'{i+1}th Max Difference: {max_diff:.5f} USDT', 
                 xy=(max_diff_time, max_diff_value_1), 
                 xytext=(max_diff_time, max_diff_value_1 + (max_diff / 2)),
                 arrowprops=dict(facecolor='red', shrink=0.05),
                 fontsize=12, color='red')
    
    # 绘制最大差异的垂直线
    plt.vlines(max_diff_time, min(max_diff_value_1, max_diff_value_2), max(max_diff_value_1, max_diff_value_2), color='red', linestyle='dotted')



plt.title(' Future price gap between platform compare - '+symbol_1+'_'+symbol_2)
plt.xlabel('Time')
plt.ylabel('Price (USDT)')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.show()





