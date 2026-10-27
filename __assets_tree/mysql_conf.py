# 数据库连接配置
import mysql.connector

mysql_config = {
    'user': 'YOUR_MYSQL_USER',
    'password': 'YOUR_MYSQL_PASSWORD',
    'host': 'YOUR_MYSQL_HOST',
    'database': 'assets',
    'raise_on_warnings': True
}

connection = mysql.connector.connect(**mysql_config)
cursor = connection.cursor(prepared=True)