# -*- coding: cp1251 -*-

import json
import pymysql
from pymongo import MongoClient

MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "cosmetics_shop",
    "autocommit": False
}
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "cosmetics_catalog"

def seed():
    with open("products.json", "r", encoding="utf-8") as f:
        products_data = json.load(f)

    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client[MONGO_DB_NAME]
    products_col = mongo_db["products"]

    mysql_conn = pymysql.connect(**MYSQL_CONFIG)

    try:
        products_col.delete_many({})
        print("Колекція MongoDB очищена.")

        products_col.create_index([("brand", 1)])
        products_col.create_index([("attributes.skin_type", 1)])
        products_col.create_index([("attributes.active_ingredients", 1)])
        products_col.create_index([("variants.variant_sku", 1)], unique=True)

        inventory_records = []

        for product in products_data:
            for variant in product.get("variants", []):
                sku = variant["variant_sku"]
                initial_stock = variant.get("initial_stock", 0)
                inventory_records.append((sku, initial_stock))

        insert_result = products_col.insert_many(products_data)
        print(f"Успішно завантажено {len(insert_result.inserted_ids)} товарів у MongoDB.")

        with mysql_conn.cursor() as cursor:
            sql_query = """
                INSERT INTO inventory (variant_sku, stock_quantity, reserved_quantity)
                VALUES (%s, %s, 0)
                ON DUPLICATE KEY UPDATE stock_quantity = VALUES(stock_quantity);
            """
            cursor.executemany(sql_query, inventory_records)
            mysql_conn.commit()

        print(f"Успішно оновлено {len(inventory_records)} товарних позицій (SKU) у MySQL.")

    except Exception as e:
        mysql_conn.rollback()
        print(f"Помилка під час ініціалізації даних: {e}")
    finally:
        mysql_conn.close()
        mongo_client.close()

if __name__ == "__main__":
    seed()
