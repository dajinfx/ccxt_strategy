# -*- coding: utf-8 -*-
"""
Created on Sun Dec  1 21:42:38 2024
@author: USER
"""

import mysql.connector
from mysql.connector import Error


class Order_db_connection:
    def __init__(self, host, user,password,database,auth_plugin):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.auth_plugin = auth_plugin

    # 配置数据库连接信息
    def insert_into(self,insert_query,data):
        try:
            # 建立连接
            connection = mysql.connector.connect(
                host=self.host,           # 数据库服务器地址
                user=self.user,           # 用户名
                password=self.password,   # 密码
                database=self.database ,  # 数据库名称
                auth_plugin=self.auth_plugin,
            )
            
            if connection.is_connected():
                print("成功连接到数据库")
                
                cursor = connection.cursor()
                
                # 调试：打印当前数据库
                cursor.execute("SELECT DATABASE();")
                db_name = cursor.fetchone()
                print("当前数据库:", db_name)
                
                # 插入数据
                if isinstance(data, list):  # 如果是多条数据，使用批量插入
                    cursor.executemany(insert_query, data)
                else:  # 单条数据
                    cursor.execute(insert_query, data)
                    
                connection.commit()
                print("插入数据成功")
                
                cursor.close()
        
        except Error as e:
            print("数据库连接失败：", e)
        
        finally:
            if connection.is_connected():
                connection.close()
                print("数据库连接已关闭")

    def query_into(self,sql):
        try:   
           # 建立连接
            connection = mysql.connector.connect(
                host=self.host,        # 数据库服务器地址
                user=self.user,             # 用户名
                password=self.password, # 密码
                database=self.database ,  # 数据库名称
                auth_plugin=self.auth_plugin
            )     

            # 查询示例
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")  # 获取当前数据库名称
            db_name = cursor.fetchone()
            print("当前数据库：", db_name)

            if connection.is_connected():
                # 查询数据示例
                cursor.execute(sql)
                rows = cursor.fetchall()
                
                print("查询结果：")
                for row in rows:
                    print(row)
                
                return rows
            return None;
        except Error as e:
            print("数据库连接失败：", e)
        
        finally:
            if connection.is_connected():
                connection.close()
                print("数据库连接已关闭")    