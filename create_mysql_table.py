#  pip install --index-url https://mirrors.aliyun.com/pypi/simple/ mysql-connector-python
import mysql.connector
from mysql.connector import Error

try:
    # 连接到数据库
    connection = mysql.connector.connect(
        host='127.0.0.1',       # 例如 'localhost' 或数据库服务器的 IP 地址
        database='stock_chat', # 数据库名
        user='root',   # 数据库用户名
        password='123456' # 数据库密码
    )

    if connection.is_connected():
        cursor = connection.cursor()

        # 创建表的 SQL 语句
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS stock_chat_record (  
            id INT AUTO_INCREMENT PRIMARY KEY,  
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
            input TEXT,  
            history TEXT,  
            output TEXT NOT NULL  
        );
        """

        # 执行 SQL 语句
        cursor.execute(create_table_sql)
        print("Table created successfully")

except Error as e:
    print(f"Error: {e}")

finally:
    # 关闭数据库连接
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")