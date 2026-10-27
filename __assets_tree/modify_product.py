from mysql_conf import connection, cursor


def insert_product(vendor_name, type_name, product_name):
    try:
        sql = f"""
        INSERT INTO product (name, vendor_id, type_id) 
        VALUES (%s, 
                (SELECT vendor.id from vendor where vendor.name=%s), 
                (SELECT type.id from type where type.name=%s))
        """
        cursor.execute(sql, (product_name, vendor_name, type_name))
        connection.commit()
        print(f"[+]成功更新 {cursor.rowcount} 条记录")
    except Exception as e:
        print(e)


def insert_product_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            insert_product(line.strip().split('_')[0].lower(), line.strip().split('_')[1].lower(), line.strip().split('_')[2].lower())


insert_product_from_txt("product.txt")