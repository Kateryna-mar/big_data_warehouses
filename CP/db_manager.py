# -*- coding: cp1251 -*-

import pymysql
from pymongo import MongoClient
from config import MYSQL_CONFIG, MONGO_CONFIG

class DatabaseManager:
    def __init__(self):
        self.sql_conn = pymysql.connect(
            **MYSQL_CONFIG,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.mongo_client = MongoClient(MONGO_CONFIG["uri"])
        self.mongo_db = self.mongo_client[MONGO_CONFIG["db_name"]]
        self.products_col = self.mongo_db["products"]

    def authenticate_user(self, email, password):
        with self.sql_conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, first_name, last_name, email, role FROM users WHERE email = %s AND password = %s",
                (email, password)
            )
            return cursor.fetchone()

    def get_staff_users(self):
        with self.sql_conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, first_name, last_name, email, phone, role 
                FROM users 
                WHERE role != 'customer'
                ORDER BY id ASC
            """)
            return cursor.fetchall()

    def create_staff_user(self, first_name, last_name, email, phone, role, password):
        with self.sql_conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, phone, role, password)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (first_name, last_name, email, phone, role, password))
        self.sql_conn.commit()

    def search_products(self, query_text=None):
        if not query_text:
            return list(self.products_col.find({}))
        regex = {"$regex": query_text.strip(), "$options": "i"}
        return list(self.products_col.find({
            "$or": [{"title": regex}, {"brand": regex}, {"variants.variant_sku": regex}]
        }))

    def add_full_product(self, brand, title, category, description, skin_types, ingredients, variants):
        doc = {
            "brand": brand,
            "title": title,
            "category": category,
            "description": description,
            "attributes": {
                "skin_type": [s.strip() for s in skin_types.split(",") if s.strip()],
                "active_ingredients": [i.strip() for i in ingredients.split(",") if i.strip()]
            },
            "variants": [
                {"variant_sku": v["sku"], "volume_ml": v["volume"], "price_uah": v["price"]}
                for v in variants
            ]
        }
        self.products_col.insert_one(doc)

        with self.sql_conn.cursor() as cursor:
            for v in variants:
                cursor.execute("""
                    INSERT INTO inventory (id, stock_quantity, reserved_quantity)
                    VALUES (%s, %s, 0)
                    ON DUPLICATE KEY UPDATE stock_quantity = stock_quantity + VALUES(stock_quantity)
                """, (v["sku"], v["stock"]))
        self.sql_conn.commit()

    def get_stock(self, sku):
        with self.sql_conn.cursor() as cursor:
            cursor.execute("SELECT stock_quantity, reserved_quantity FROM inventory WHERE id = %s", (sku,))
            return cursor.fetchone()

    def update_stock(self, sku, add_quantity):
        with self.sql_conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO inventory (id, stock_quantity, reserved_quantity)
                VALUES (%s, %s, 0)
                ON DUPLICATE KEY UPDATE stock_quantity = stock_quantity + %s
            """, (sku, add_quantity, add_quantity))
        self.sql_conn.commit()

    def get_all_inventory_status(self):
        with self.sql_conn.cursor() as cursor:
            cursor.execute("SELECT id, stock_quantity, reserved_quantity FROM inventory ORDER BY stock_quantity ASC")
            return cursor.fetchall()

    def get_orders_list(self):
        with self.sql_conn.cursor() as cursor:
            cursor.execute("""
                SELECT o.id, CONCAT(u.first_name, ' ', u.last_name) as customer, u.phone, o.status,
                       COALESCE(SUM(oi.quantity * oi.unit_price), 0.00) as total_amount
                FROM orders o
                JOIN users u ON o.user_id = u.id
                LEFT JOIN order_items oi ON o.id = oi.order_id
                GROUP BY o.id, customer, u.phone, o.status
                ORDER BY o.id DESC LIMIT 30
            """)
            return cursor.fetchall()

    def create_order(self, user_id: int, items: list):
        cursor = self.sql_conn.cursor()
        try:
            cursor.execute("INSERT INTO orders (user_id, status) VALUES (%s, 'PAID')", (user_id,))
            order_id = cursor.lastrowid

            for item in items:
                cursor.execute("SELECT stock_quantity FROM inventory WHERE id = %s FOR UPDATE", (item['sku'],))
                row = cursor.fetchone()
                if not row or row['stock_quantity'] < item['qty']:
                    raise ValueError(f"Недостатньо товару на складі: {item['sku']}")

                cursor.execute(
                    "UPDATE inventory SET stock_quantity = stock_quantity - %s WHERE id = %s",
                    (item['qty'], item['sku'])
                )
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, unit_price, quantity) VALUES (%s, %s, %s, %s)",
                    (order_id, item['sku'], item['price'], item['qty'])
                )

            self.sql_conn.commit()
            return order_id
        except Exception as e:
            self.sql_conn.rollback()
            raise e
        finally:
            cursor.close()

    def get_kpi_metrics(self):
        try:
            with self.sql_conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        COALESCE(SUM(oi.quantity * oi.unit_price), 0.00) as total_revenue,
                        COUNT(DISTINCT o.id) as total_orders
                    FROM orders o
                    LEFT JOIN order_items oi ON o.id = oi.order_id
                    WHERE o.status = 'PAID'
                """)
                stats = cursor.fetchone()
                rev = float(stats["total_revenue"]) if stats and stats["total_revenue"] else 0.0
                orders_cnt = int(stats["total_orders"]) if stats and stats["total_orders"] else 0
                avg_chk = (rev / orders_cnt) if orders_cnt > 0 else 0.0

            total_products = self.products_col.count_documents({})
            return {"revenue": rev, "orders": orders_cnt, "avg_check": avg_chk, "products_count": total_products}
        except Exception:
            return {"revenue": 0.0, "orders": 0, "avg_check": 0.0, "products_count": 0}

    def get_sales_by_date(self):
        with self.sql_conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    DATE(o.created_at) as order_date,
                    COUNT(DISTINCT o.id) as orders_count,
                    COALESCE(SUM(oi.quantity * oi.unit_price), 0.00) as daily_revenue
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.status = 'PAID'
                GROUP BY DATE(o.created_at)
                ORDER BY order_date ASC
            """)
            return cursor.fetchall()

    def get_top_selling_products(self):
        with self.sql_conn.cursor() as cursor:
            cursor.execute("""
                SELECT product_id, SUM(quantity) as total_sold
                FROM order_items
                GROUP BY product_id
                ORDER BY total_sold DESC LIMIT 5
            """)
            return cursor.fetchall()

    def get_order_status_distribution(self):
        with self.sql_conn.cursor() as cursor:
            cursor.execute("SELECT status, COUNT(*) as count FROM orders GROUP BY status")
            return cursor.fetchall()

    def get_category_distribution(self):
        pipeline = [{"$group": {"_id": "$category", "count": {"$sum": 1}}}]
        return list(self.products_col.aggregate(pipeline))