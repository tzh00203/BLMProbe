# 数据库连接配置
import mysql.connector

mysql_config = {
    'user': 'root',
    'password': 'zhang@ns78r+nuo',
    'host': '121.36.55.115',
    'database': 'assets',
    'raise_on_warnings': True
}

connection = mysql.connector.connect(**mysql_config)
cursor = connection.cursor(prepared=True)