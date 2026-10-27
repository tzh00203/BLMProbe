from mysql_conf import connection, cursor


def select_vendor(vendor_id=None, vendor_name=None):
    try:
        if vendor_id:
            sql = f"SELECT * FROM vendor WHERE id = %s"
            cursor.execute(sql,(vendor_id,))
        elif vendor_name:
            sql = f"SELECT * FROM vendor WHERE name = %s"
            cursor.execute(sql,(vendor_name,))
        else:
            print("[+]缺少查询条件")

        # 打印查询结果
        for (id, name) in cursor:
            print(f"id: {id}, name: {name}")

    except Exception as e:
        print(e)


def insert_vendor(vendor_name):
    try:
        sql = "INSERT INTO vendor (name) VALUES (%s)"
        cursor.execute(sql, (vendor_name,))
        connection.commit()
        print(f"[+]成功更新 {cursor.rowcount} 条记录")

    except Exception as e:
        print(e)


def insert_vendor_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            insert_vendor(line.strip().lower())



insert_vendor_from_txt("vendor.txt")