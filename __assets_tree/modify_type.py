from mysql_conf import connection, cursor

def select_type(type_id=None, type_name=None):
    try:

        if type_id:
            query = "SELECT * FROM `type` WHERE id = {type_id}"
            cursor.execute(query)
        elif type_name:
            query = f"SELECT * FROM type WHERE name = '{type_name}'"
            cursor.execute(query)
        else:
            query = "SELECT * FROM type"
            cursor.execute(query)

        # 打印查询结果
        for (id, name) in cursor:
            print(f"id: {id}, name: {name}")

    except Exception as e:
        print(e)


def insert_type(type_name):
    try:
        sql = "INSERT INTO type (name) VALUES (%s)"
        cursor.execute(sql, (type_name,))
        connection.commit()
        print(f"[+]成功更新 {cursor.rowcount} 条记录")

    except Exception as e:
        print(e)


def insert_type_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            insert_type(line.strip().lower())


insert_type_from_txt("type.txt")