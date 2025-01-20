import datetime
import pickle
import threading

import mysql.connector
from mysql.connector import Error


# 创建数据库连接
def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


# 执行SQL查询
def execute_query(connection, query, params=None):
    cursor = connection.cursor()
    try:
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


# 插入数据到stock_history表
def insert_into_stock_history(session, input_data, output_data, history_data):
    # 替换为你的MySQL数据库连接信息
    host_name = "127.0.0.1"  # 或你的数据库服务器地址
    user_name = "root"  # 或你的数据库用户名
    user_password = "123456"  # 或你的数据库密码
    db_name = "stock_chat"  # 或你的数据库名

    # 创建数据库连接
    connection = create_connection(host_name, user_name, user_password, db_name)

    query = """INSERT INTO stock_history (session, input, output, his) VALUES (%s, %s, %s, %s)"""
    params = (session, input_data, output_data, history_data)
    execute_query(connection, query, params)

    if connection.is_connected():
        connection.close()


# 查询stock_history表中的所有数据
def query_latest_stock_history(session):
    # 替换为你的MySQL数据库连接信息
    host_name = "127.0.0.1"  # 或你的数据库服务器地址
    user_name = "root"  # 或你的数据库用户名
    user_password = "123456"  # 或你的数据库密码
    db_name = "stock_chat"  # 或你的数据库名

    # 创建数据库连接
    connection = create_connection(host_name, user_name, user_password, db_name)

    query = """
    SELECT * FROM stock_history
    WHERE session = %s
    ORDER BY time DESC
    LIMIT 1
    """
    cursor = connection.cursor(dictionary=True)  # 使用dictionary=True以便返回字典格式的结果
    cursor.execute(query, (session,))
    row = cursor.fetchone()  # fetchone()返回查询结果的第一行

    if connection.is_connected():
        cursor.close()
        connection.close()

    return row


# 主函数
def main():
    # 插入数据
    session = "example_session"
    input_data = str(datetime.datetime.now())
    output_data = "example_output"

    # 假设history是一个二进制对象，这里用bytes类型的数据代替
    # history_data = b"example_binary_data"
    data = [
        {"name": "Alice", "age": 30, "city": "New York"},
        {"name": "Bob", "age": 25, "city": "Los Angeles"},
        {"name": "Charlie", "age": 35, "city": "Chicago"}
    ]

    # 将列表序列化为二进制字节串并存储在变量中
    history_data = pickle.dumps(data)

    db_thread = threading.Thread(target=insert_into_stock_history, args=(session, input_data, output_data, history_data))
    db_thread.start()
    db_thread.join()

    # 查询数据
    session_to_query = "example_session"  # 替换为你要查询的session
    latest_record = query_latest_stock_history(session_to_query)

    if latest_record:
        print("Latest record for session '{}':".format(session_to_query))
        for key, value in latest_record.items():
            if key != 'his':
                print("{}: {}".format(key, value))
            else:
                loaded_his = pickle.loads(value)
                print(loaded_his)


# 运行主函数
if __name__ == "__main__":
    main()
