import mysql.connector
from mysql.connector import Error
import threading


# 数据库插入函数，接受参数
def insert_record_into_database(input_data, history_data, output_data):
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            database='stock_chat',
            user='root',
            password='123456'
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # 插入记录的SQL语句
            insert_record_sql = """  
            INSERT INTO stock_chat_record (input, history, output) VALUES (%s, %s, %s)  
            """

            # 执行插入记录的SQL语句
            cursor.execute(insert_record_sql, (input_data, history_data, output_data))
            connection.commit()
            print(f"1 record inserted successfully.")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")

        # 主流程


def main():
    # 要插入的数据
    input_data = "User input example"
    history_data = "History example"
    output_data = "Bot output example"

    # 创建一个线程来执行数据库插入操作
    db_thread = threading.Thread(target=insert_record_into_database, args=(input_data, history_data, output_data))

    # 启动线程
    db_thread.start()

    # 等待线程完成
    db_thread.join()

    print("Database insertion thread has finished.")


# 运行主流程
if __name__ == "__main__":
    main()