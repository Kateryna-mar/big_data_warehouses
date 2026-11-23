# -*- coding: utf-8 -*-

import customtkinter as ctk
from tkinter import messagebox
from db_manager import DatabaseManager

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class CosmeticsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Система автоматизації інтернет-магазину косметики")
        self.geometry("1150x780")
        ctk.set_appearance_mode("System")

        self.db = DatabaseManager()
        self.current_user = None

        self.show_login_screen()

    def show_login_screen(self):
        for w in self.winfo_children():
            w.destroy()

        box = ctk.CTkFrame(self, width=420, height=380, corner_radius=12)
        box.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(box, text="Вхід до системи", font=("Arial", 20, "bold")).pack(pady=(30, 20))

        self.login_email = ctk.CTkEntry(box, placeholder_text="Email", width=320)
        self.login_email.pack(pady=10)
        self.login_email.insert(0, "admin@shop.ua")

        self.login_pwd = ctk.CTkEntry(box, placeholder_text="Пароль", show="*", width=320)
        self.login_pwd.pack(pady=10)
        self.login_pwd.insert(0, "admin123")

        ctk.CTkButton(box, text="Увійти", command=self.handle_login, width=320).pack(pady=20)

    def handle_login(self):
        user = self.db.authenticate_user(self.login_email.get().strip(), self.login_pwd.get().strip())
        if not user:
            messagebox.showerror("Помилка", "Неправильний email або пароль!")
            return
        self.current_user = user
        self.show_workspace()

    def show_workspace(self):
        for w in self.winfo_children():
            w.destroy()

        role = self.current_user["role"]
        name = f"{self.current_user['first_name']} {self.current_user['last_name']}"

        top = ctk.CTkFrame(self, height=45, corner_radius=0)
        top.pack(fill="x", padx=10, pady=(5, 0))

        roles_dict = {
            "admin": "Адміністратор",
            "order_manager": "Менеджер замовлень",
            "catalog_manager": "Контент / Склад-менеджер"
        }
        ctk.CTkLabel(top, text=roles_dict.get(role, role), font=("Arial", 13, "bold")).pack(side="left", padx=15)
        ctk.CTkButton(top, text="Вийти", width=80, height=28, fg_color="#c0392b", command=self.show_login_screen).pack(side="right", padx=15, pady=8)

        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=5)

        if role in ["admin", "order_manager", "catalog_manager"]:
            self.tab_cat = self.tabs.add("Каталог")
            self.build_catalog_tab()

        if role in ["admin", "order_manager"]:
            self.tab_ord = self.tabs.add("Замовлення")
            self.build_orders_tab()

        if role in ["admin", "catalog_manager"]:
            self.tab_inv = self.tabs.add("Склад / Додавання")
            self.build_inventory_tab()

        if role == "admin":
            self.tab_usr = self.tabs.add("Персонал")
            self.build_users_tab()

        if role in ["admin", "order_manager", "catalog_manager"]:
            self.tab_anl = self.tabs.add("Аналітика")
            self.build_analytics_tab()

    def build_catalog_tab(self):
        bar = ctk.CTkFrame(self.tab_cat)
        bar.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(bar, text="Пошук:").pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(bar, placeholder_text="Введіть назву, бренд або код ...", width=420)
        self.search_entry.pack(side="left", padx=5)

        ctk.CTkButton(bar, text="Знайти", command=self.refresh_catalog).pack(side="left", padx=5)
        ctk.CTkButton(bar, text="Скинути", command=lambda: [self.search_entry.delete(0, "end"), self.refresh_catalog()]).pack(side="left", padx=5)

        self.catalog_box = ctk.CTkTextbox(self.tab_cat, width=1100, height=560)
        self.catalog_box.pack(padx=10, pady=10, fill="both", expand=True)
        self.refresh_catalog()

    def refresh_catalog(self):
        query = self.search_entry.get().strip() or None
        products = self.db.search_products(query_text=query)

        self.catalog_box.delete("1.0", "end")
        if not products:
            self.catalog_box.insert("end", "Товарів не знайдено.\n")
            return

        for p in products:
            self.catalog_box.insert("end", f"Товар: {p.get('brand')} — {p.get('title')} [{p.get('category', 'Без категорії')}]\n")
            self.catalog_box.insert("end", f"  Опис: {p.get('description', '')}\n")
            self.catalog_box.insert("end", f"  Активні компоненти: {', '.join(p.get('attributes', {}).get('active_ingredients', []))}\n")
            self.catalog_box.insert("end", "  Доступні варіанти:\n")
            for v in p.get("variants", []):
                sku = v["variant_sku"]
                stock = self.db.get_stock(sku)
                qty = stock["stock_quantity"] if stock else 0
                res = stock["reserved_quantity"] if stock else 0
                self.catalog_box.insert(
                    "end",
                    f"    • SKU: {sku:<14} | Об'єм: {v.get('volume_ml')} мл | Ціна: {v['price_uah']} грн | Залишок: {qty} шт. (Резерв: {res})\n"
                )
            self.catalog_box.insert("end", "-" * 100 + "\n")

    def build_orders_tab(self):
        split = ctk.CTkFrame(self.tab_ord)
        split.pack(fill="both", expand=True, padx=10, pady=10)

        left = ctk.CTkFrame(split, width=380)
        left.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(left, text="Створення замовлення", font=("Arial", 15, "bold")).pack(pady=10)
        self.o_uid = ctk.CTkEntry(left, placeholder_text="ID клієнта (напр. 1)", width=320)
        self.o_uid.insert(0, "1")
        self.o_uid.pack(pady=6)

        self.o_sku = ctk.CTkEntry(left, placeholder_text="Артикул", width=320)
        self.o_sku.pack(pady=6)

        self.o_price = ctk.CTkEntry(left, placeholder_text="Ціна (грн)", width=320)
        self.o_price.pack(pady=6)

        self.o_qty = ctk.CTkEntry(left, placeholder_text="Кількість (шт)", width=320)
        self.o_qty.pack(pady=6)

        ctk.CTkButton(left, text="Провести замовлення", command=self.action_create_order).pack(pady=15)

        right = ctk.CTkFrame(split)
        right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(right, text="Останні замовлення клієнтів", font=("Arial", 15, "bold")).pack(pady=5)
        self.orders_box = ctk.CTkTextbox(right, height=500)
        self.orders_box.pack(fill="both", expand=True, padx=5, pady=5)
        self.refresh_orders()

    def refresh_orders(self):
        orders = self.db.get_orders_list()
        self.orders_box.delete("1.0", "end")
        for o in orders:
            self.orders_box.insert(
                "end",
                f"Замовлення #{o['id']:<3} | Клієнт: {o['customer']:<22} | Тел: {o['phone']:<14} | Статус: {o['status']:<9} | Сума: {o['total_amount']:>7.2f} грн\n"
            )

    def action_create_order(self):
        try:
            uid = int(self.o_uid.get().strip())
            sku = self.o_sku.get().strip()
            price = float(self.o_price.get().strip())
            qty = int(self.o_qty.get().strip())

            order_id = self.db.create_order(user_id=uid, items=[{'sku': sku, 'price': price, 'qty': qty}])
            messagebox.showinfo("Успіх", f"Замовлення #{order_id} проведено! Залишок списано.")
            self.refresh_orders()
            if hasattr(self, 'catalog_box'):
                self.refresh_catalog()
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def build_inventory_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_inv, width=1050, height=580)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(scroll, text="1. Поповнення складу", font=("Arial", 15, "bold")).pack(anchor="w", pady=5)
        r_box = ctk.CTkFrame(scroll)
        r_box.pack(fill="x", pady=5)

        self.r_sku = ctk.CTkEntry(r_box, placeholder_text="SKU (id у таблиці inventory)")
        self.r_sku.pack(side="left", padx=8, pady=8)

        self.r_qty = ctk.CTkEntry(r_box, placeholder_text="+ Кількість (шт)")
        self.r_qty.pack(side="left", padx=8, pady=8)

        ctk.CTkButton(r_box, text="Поповнити залишок", command=self.action_restock).pack(side="left", padx=10, pady=8)

        ctk.CTkLabel(scroll, text="").pack(pady=5)
        ctk.CTkLabel(scroll, text="2. Реєстрація нового товару", font=("Arial", 15, "bold")).pack(anchor="w", pady=5)
        p_box = ctk.CTkFrame(scroll)
        p_box.pack(fill="x", pady=5)

        self.p_brand = ctk.CTkEntry(p_box, placeholder_text="Бренд", width=450)
        self.p_brand.pack(pady=4, padx=10, anchor="w")
        self.p_title = ctk.CTkEntry(p_box, placeholder_text="Назва товару", width=450)
        self.p_title.pack(pady=4, padx=10, anchor="w")
        self.p_cat = ctk.CTkEntry(p_box, placeholder_text="Категорія", width=450)
        self.p_cat.pack(pady=4, padx=10, anchor="w")
        self.p_desc = ctk.CTkEntry(p_box, placeholder_text="Опис", width=450)
        self.p_desc.pack(pady=4, padx=10, anchor="w")
        self.p_skin = ctk.CTkEntry(p_box, placeholder_text="Типи шкіри через кому", width=450)
        self.p_skin.pack(pady=4, padx=10, anchor="w")
        self.p_ingr = ctk.CTkEntry(p_box, placeholder_text="Активні інгредієнти через кому", width=450)
        self.p_ingr.pack(pady=4, padx=10, anchor="w")

        ctk.CTkLabel(p_box, text="Параметри упаковки:", font=("Arial", 12, "bold")).pack(pady=5, padx=10, anchor="w")
        self.p_sku = ctk.CTkEntry(p_box, placeholder_text="Артикул SKU", width=300)
        self.p_sku.pack(pady=3, padx=10, anchor="w")
        self.p_vol = ctk.CTkEntry(p_box, placeholder_text="Об'єм (мл)", width=300)
        self.p_vol.pack(pady=3, padx=10, anchor="w")
        self.p_price = ctk.CTkEntry(p_box, placeholder_text="Ціна (грн)", width=300)
        self.p_price.pack(pady=3, padx=10, anchor="w")
        self.p_stock = ctk.CTkEntry(p_box, placeholder_text="Початкова кількість на складі", width=300)
        self.p_stock.pack(pady=3, padx=10, anchor="w")

        ctk.CTkButton(p_box, text="Зберегти товар", command=self.action_add_product).pack(pady=12, padx=10, anchor="w")

    def action_restock(self):
        sku = self.r_sku.get().strip()
        qty = self.r_qty.get().strip()
        if not sku or not qty:
            messagebox.showwarning("Увага", "Заповніть SKU та кількість!")
            return
        try:
            self.db.update_stock(sku, int(qty))
            messagebox.showinfo("Успіх", f"Залишок {sku} поповнено на +{qty} шт.")
            if hasattr(self, 'catalog_box'):
                self.refresh_catalog()
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def action_add_product(self):
        try:
            b = self.p_brand.get().strip()
            t = self.p_title.get().strip()
            c = self.p_cat.get().strip()
            d = self.p_desc.get().strip()
            s = self.p_skin.get().strip()
            i = self.p_ingr.get().strip()

            sku = self.p_sku.get().strip()
            vol = int(self.p_vol.get().strip())
            pr = float(self.p_price.get().strip())
            st = int(self.p_stock.get().strip())

            self.db.add_full_product(b, t, c, d, s, i, [{"sku": sku, "volume": vol, "price": pr, "stock": st}])
            messagebox.showinfo("Успіх", f"Товар '{t}' додано в MongoDB, а {sku} — у MySQL!")
            if hasattr(self, 'catalog_box'):
                self.refresh_catalog()
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def build_users_tab(self):
        split = ctk.CTkFrame(self.tab_usr)
        split.pack(fill="both", expand=True, padx=10, pady=10)

        left = ctk.CTkFrame(split, width=380)
        left.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(left, text="Додати співробітника", font=("Arial", 15, "bold")).pack(pady=10)
        self.u_fn = ctk.CTkEntry(left, placeholder_text="Ім'я", width=320)
        self.u_fn.pack(pady=5)
        self.u_ln = ctk.CTkEntry(left, placeholder_text="Прізвище", width=320)
        self.u_ln.pack(pady=5)
        self.u_em = ctk.CTkEntry(left, placeholder_text="Email", width=320)
        self.u_em.pack(pady=5)
        self.u_ph = ctk.CTkEntry(left, placeholder_text="Телефон", width=320)
        self.u_ph.pack(pady=5)
        self.u_rl = ctk.CTkOptionMenu(left, values=["order_manager", "catalog_manager", "admin"], width=320)
        self.u_rl.pack(pady=5)
        self.u_pw = ctk.CTkEntry(left, placeholder_text="Пароль", width=320)
        self.u_pw.pack(pady=5)

        ctk.CTkButton(left, text="Створити запис", command=self.action_create_user).pack(pady=15)

        right = ctk.CTkFrame(split)
        right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(right, text="Персонал системи", font=("Arial", 15, "bold")).pack(pady=5)
        self.users_box = ctk.CTkTextbox(right, height=500)
        self.users_box.pack(fill="both", expand=True, padx=5, pady=5)
        self.refresh_users()

    def refresh_users(self):
        staff = self.db.get_staff_users()
        self.users_box.delete("1.0", "end")
        for u in staff:
            self.users_box.insert(
                "end",
                f"ID: {u['id']:<3} | {u['first_name']} {u['last_name']:<20} | Роль: {u['role']:<16} | Email: {u['email']}\n"
            )

    def action_create_user(self):
        try:
            self.db.create_staff_user(
                self.u_fn.get().strip(), self.u_ln.get().strip(), self.u_em.get().strip(),
                self.u_ph.get().strip(), self.u_rl.get(), self.u_pw.get().strip()
            )
            messagebox.showinfo("Успіх", "Співробітника успішно додано!")
            self.refresh_users()
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def build_analytics_tab(self):
        top_ctrl = ctk.CTkFrame(self.tab_anl)
        top_ctrl.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(top_ctrl, text="Оновити аналітику", command=self.refresh_analytics).pack(side="left", padx=10, pady=5)

        self.kpi_box = ctk.CTkFrame(self.tab_anl)
        self.kpi_box.pack(fill="x", padx=10, pady=5)

        self.chart_box = ctk.CTkScrollableFrame(self.tab_anl, height=520)
        self.chart_box.pack(fill="both", expand=True, padx=10, pady=5)

        self.refresh_analytics()

    def refresh_analytics(self):
        for w in self.kpi_box.winfo_children():
            w.destroy()

        kpi = self.db.get_kpi_metrics()
        kpis = [
            ("Загальний виторг", f"{kpi['revenue']:,.2f} грн", "#2980b9"),
            ("Оплачених замовлень", f"{kpi['orders']} шт.", "#27ae60"),
            ("Середній чек", f"{kpi['avg_check']:,.2f} грн", "#8e44ad"),
            ("Товарів у каталозі", f"{kpi['products_count']} од.", "#d35400")
        ]
        for title, val, color in kpis:
            card = ctk.CTkFrame(self.kpi_box, corner_radius=8, fg_color=color)
            card.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            ctk.CTkLabel(card, text=title, font=("Arial", 11), text_color="#ecf0f1").pack(pady=(6, 2))
            ctk.CTkLabel(card, text=val, font=("Arial", 15, "bold"), text_color="white").pack(pady=(0, 6))

        for w in self.chart_box.winfo_children():
            w.destroy()
        plt.close("all")

        role = self.current_user["role"]

        if role == "admin":
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 6), dpi=90)
            plt.subplots_adjust(wspace=0.35, hspace=0.45, bottom=0.12, top=0.92)

            daily = self.db.get_sales_by_date()
            if daily:
                ax1.plot([str(d["order_date"]) for d in daily], [float(d["daily_revenue"]) for d in daily], marker="o", color="#2980b9")
                ax1.set_title("Динаміка виторгу по днях", fontsize=10)
                ax1.tick_params(axis="x", rotation=25)
                ax1.grid(True, linestyle="--", alpha=0.5)
            else:
                ax1.text(0.5, 0.5, "Немає замовлень", ha="center")

            top = self.db.get_top_selling_products()
            if top:
                ax2.bar([str(i["product_id"]) for i in top], [int(i["total_sold"]) for i in top], color="#27ae60")
                ax2.set_title("Топ-5 товарів (шт)", fontsize=10)
                ax2.tick_params(axis="x", rotation=25)
            else:
                ax2.text(0.5, 0.5, "Немає даних", ha="center")

            statuses = self.db.get_order_status_distribution()
            if statuses:
                ax3.bar([str(s["status"]) for s in statuses], [int(s["count"]) for s in statuses], color=["#2ecc71", "#f39c12", "#e74c3c"])
                ax3.set_title("Статуси замовлень", fontsize=10)
            else:
                ax3.text(0.5, 0.5, "Немає даних", ha="center")

            cats = self.db.get_category_distribution()
            if cats:
                ax4.pie([int(c["count"]) for c in cats], labels=[str(c["_id"]) if c["_id"] else "Інше" for c in cats], autopct="%1.0f%%", startangle=140)
                ax4.set_title("Категорії", fontsize=10)
            else:
                ax4.text(0.5, 0.5, "Каталог порожній", ha="center")

        elif role == "order_manager":
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), dpi=90)
            daily = self.db.get_sales_by_date()
            if daily:
                ax1.plot([str(d["order_date"]) for d in daily], [int(d["orders_count"]) for d in daily], marker="s", color="#e67e22")
                ax1.set_title("Кількість покупок по днях", fontsize=11)
                ax1.tick_params(axis="x", rotation=25)
                ax1.grid(True, linestyle="--", alpha=0.5)
            else:
                ax1.text(0.5, 0.5, "Немає даних", ha="center")

            statuses = self.db.get_order_status_distribution()
            if statuses:
                ax2.bar([str(s["status"]) for s in statuses], [int(s["count"]) for s in statuses], color=["#2ecc71", "#f39c12", "#c0392b"])
                ax2.set_title("Статуси замовлень", fontsize=11)
            else:
                ax2.text(0.5, 0.5, "Немає даних", ha="center")

        elif role == "catalog_manager":
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), dpi=90)
            stocks = self.db.get_all_inventory_status()
            if stocks:
                qtys = [int(s["stock_quantity"]) for s in stocks[:8]]
                colors = ["#e74c3c" if q < 10 else "#2ecc71" for q in qtys]
                ax1.bar([str(s["id"]) for s in stocks[:8]], qtys, color=colors)
                ax1.set_title("Контроль залишків (< 10 шт.)", fontsize=11)
                ax1.tick_params(axis="x", rotation=35)
            else:
                ax1.text(0.5, 0.5, "Склад порожній", ha="center")

            cats = self.db.get_category_distribution()
            if cats:
                ax2.pie([int(c["count"]) for c in cats], labels=[str(c["_id"]) if c["_id"] else "Інше" for c in cats], autopct="%1.1f%%", startangle=140)
                ax2.set_title("Частки категорій", fontsize=11)
            else:
                ax2.text(0.5, 0.5, "Каталог порожній", ha="center")

        canvas = FigureCanvasTkAgg(fig, master=self.chart_box)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=5)

if __name__ == "__main__":
    app = CosmeticsApp()
    app.mainloop()