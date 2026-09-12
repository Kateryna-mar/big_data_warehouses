using System;
using System.Data.SQLite;

namespace Lab_1_SQLite
{
    class Program
    {
        static void Main(string[] args)
        {
            string dbPath = "Data Source=Shop.db;Version=3;";
            using (SQLiteConnection connection = new SQLiteConnection(dbPath))
            {
                connection.Open();

                using (var cmdPragma = new SQLiteCommand("PRAGMA foreign_keys = ON;", connection))
                {
                    cmdPragma.ExecuteNonQuery();
                }

                InitializeDatabase(connection);
                menu_go(connection);
            }
        }

        static void InitializeDatabase(SQLiteConnection m_dbConnection)
        {
            string sqlCategory = @"CREATE TABLE IF NOT EXISTS Category (
                                    id INTEGER PRIMARY KEY,
                                    name TEXT NOT NULL,
                                    description TEXT
                                  );";

            string sqlProduct = @"CREATE TABLE IF NOT EXISTS Product (
                                    id INTEGER PRIMARY KEY,
                                    name TEXT NOT NULL,
                                    price REAL,
                                    unit TEXT,
                                    category_id INTEGER,
                                    FOREIGN KEY (category_id) REFERENCES Category(id)
                                        ON DELETE SET NULL
                                        ON UPDATE CASCADE
                                  );";

            using (var cmd = new SQLiteCommand(sqlCategory, m_dbConnection))
                cmd.ExecuteNonQuery();

            using (var cmd = new SQLiteCommand(sqlProduct, m_dbConnection))
                cmd.ExecuteNonQuery();
        }

        public static void menu_go(SQLiteConnection m_dbConnection)
        {
            Console.WriteLine("\n=== ГОЛОВНЕ МЕНЮ ===");
            Console.WriteLine("1 - Додавання запису");
            Console.WriteLine("2 - Оновлення значення");
            Console.WriteLine("3 - Видалення рядків");
            Console.WriteLine("4 - Перегляд таблиць");
            Console.WriteLine("5 - Вихід");
            Console.Write("Оберіть режим роботи: ");

            string menu = Console.ReadLine();
            int menu1;
            if (!int.TryParse(menu, out menu1))
            {
                Console.WriteLine("Некоректний вибір.");
                menu_go(m_dbConnection);
                return;
            }

            if (menu1 == 1)
            {
                Console.WriteLine("\nОберіть таблицю для роботи:");
                Console.WriteLine("1 - Категорія (Category)\n2 - Товар (Product)");
                int choice = int.Parse(Console.ReadLine());

                Console.Write("Введіть кількість нових записів: ");
                int count = int.Parse(Console.ReadLine());

                if (choice == 1)
                {
                    for (int i = 0; i < count; i++)
                    {
                        Console.WriteLine($"\nВведіть дані для {i + 1}-ї категорії:");
                        Console.Write("ID категорії: ");
                        int idCat = int.Parse(Console.ReadLine());
                        Console.Write("Назва: ");
                        string name = Console.ReadLine();
                        Console.Write("Опис: ");
                        string desc = Console.ReadLine();

                        string sql = "INSERT INTO Category (id, name, description) VALUES (@id, @name, @desc);";
                        using (var cmd = new SQLiteCommand(sql, m_dbConnection))
                        {
                            cmd.Parameters.AddWithValue("@id", idCat);
                            cmd.Parameters.AddWithValue("@name", name);
                            cmd.Parameters.AddWithValue("@desc", desc);
                            cmd.ExecuteNonQuery();
                        }
                    }
                }
                else if (choice == 2)
                {
                    for (int i = 0; i < count; i++)
                    {
                        Console.WriteLine($"\nВведіть дані для {i + 1}-го товару:");
                        Console.Write("ID товару: ");
                        int idProd = int.Parse(Console.ReadLine());
                        Console.Write("Назва товару: ");
                        string name = Console.ReadLine();
                        Console.Write("Ціна: ");
                        double price = double.Parse(Console.ReadLine());
                        Console.Write("Одиниця вимірювання (шт, кг тощо): ");
                        string unit = Console.ReadLine();
                        Console.Write("ID категорії (FK): ");
                        int idCat = int.Parse(Console.ReadLine());

                        string sql = "INSERT INTO Product (id, name, price, unit, category_id) VALUES (@id, @name, @price, @unit, @idCat);";

                        using (var cmd = new SQLiteCommand(sql, m_dbConnection))
                        {
                            cmd.Parameters.AddWithValue("@id", idProd);
                            cmd.Parameters.AddWithValue("@name", name);
                            cmd.Parameters.AddWithValue("@price", price);
                            cmd.Parameters.AddWithValue("@unit", unit);
                            cmd.Parameters.AddWithValue("@idCat", idCat);

                            try
                            {
                                cmd.ExecuteNonQuery();
                                Console.WriteLine("Товар успішно додано.");
                            }
                            catch (SQLiteException ex) when (ex.ResultCode == SQLiteErrorCode.Constraint_ForeignKey || ex.Message.Contains("FOREIGN KEY"))
                            {
                                Console.WriteLine($"\n[Помилка зовнішнього ключа]: Категорії з ID = {idCat} не існує в головній таблиці Category!");
                                Console.WriteLine("Операцію додавання товару скасовано.\n");
                            }
                            catch (SQLiteException ex) when (ex.ResultCode == SQLiteErrorCode.Constraint_PrimaryKey || ex.Message.Contains("UNIQUE"))
                            {
                                Console.WriteLine($"\n[Помилка первинного ключа]: Товар з ID = {idProd} вже існує!");
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine($"\nНепередбачена помилка: {ex.Message}");
                            }
                        }
                    }
                }
                menu_go(m_dbConnection);
            }
            else if (menu1 == 2)
            {
                Console.WriteLine("\nОберіть таблицю для оновлення:");
                Console.WriteLine("1 - Категорія (зміна ID)\n2 - Товар (зміна ціни)");
                int choice = int.Parse(Console.ReadLine());

                if (choice == 1)
                {
                    Console.Write("Введіть старий ID категорії: ");
                    int oldId = int.Parse(Console.ReadLine());
                    Console.Write("Введіть новий ID категорії: ");
                    int newId = int.Parse(Console.ReadLine());

                    string sql = "UPDATE Category SET id = @newId WHERE id = @oldId;";
                    using (var cmd = new SQLiteCommand(sql, m_dbConnection))
                    {
                        cmd.Parameters.AddWithValue("@newId", newId);
                        cmd.Parameters.AddWithValue("@oldId", oldId);
                        cmd.ExecuteNonQuery();
                    }
                    Console.WriteLine("ID категорії оновлено.");
                }
                else if (choice == 2)
                {
                    Console.Write("Введіть ID товару для оновлення: ");
                    int idProd = int.Parse(Console.ReadLine());
                    Console.Write("Введіть нову ціну: ");
                    double newPrice = double.Parse(Console.ReadLine());

                    string sql = "UPDATE Product SET price = @price WHERE id = @id;";
                    using (var cmd = new SQLiteCommand(sql, m_dbConnection))
                    {
                        cmd.Parameters.AddWithValue("@price", newPrice);
                        cmd.Parameters.AddWithValue("@id", idProd);
                        cmd.ExecuteNonQuery();
                    }
                    Console.WriteLine("Ціну товару оновлено.");
                }
                menu_go(m_dbConnection);
            }
            else if (menu1 == 3)
            {
                Console.WriteLine("\nОберіть таблицю для видалення рядків:");
                Console.WriteLine("1 - Категорія\n2 - Товар");
                int choice = int.Parse(Console.ReadLine());

                if (choice == 1)
                {
                    Console.Write("Введіть ID категорії для видалення: ");
                    int idCat = int.Parse(Console.ReadLine());

                    string sql = "DELETE FROM Category WHERE id = @id;";
                    using (var cmd = new SQLiteCommand(sql, m_dbConnection))
                    {
                        cmd.Parameters.AddWithValue("@id", idCat);
                        cmd.ExecuteNonQuery();
                    }
                    Console.WriteLine("Категорію видалено.");
                }
                else if (choice == 2)
                {
                    Console.Write("Введіть ID товару для видалення: ");
                    int idProd = int.Parse(Console.ReadLine());

                    string sql = "DELETE FROM Product WHERE id = @id;";
                    using (var cmd = new SQLiteCommand(sql, m_dbConnection))
                    {
                        cmd.Parameters.AddWithValue("@id", idProd);
                        cmd.ExecuteNonQuery();
                    }
                    Console.WriteLine("Товар видалено.");
                }
                menu_go(m_dbConnection);
            }
            else if (menu1 == 4)
            {
                Console.WriteLine("\n--- Вміст таблиці Category ---");
                using (var cmd = new SQLiteCommand("SELECT * FROM Category;", m_dbConnection))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        Console.WriteLine($"ID: {reader["id"]} | Назва: {reader["name"]} | Опис: {reader["description"]}");
                    }
                }

                Console.WriteLine("\n--- Вміст таблиці Product ---");
                using (var cmd = new SQLiteCommand("SELECT * FROM Product;", m_dbConnection))
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        string catVal = reader["category_id"] == DBNull.Value ? "NULL" : reader["category_id"].ToString();
                        Console.WriteLine($"ID: {reader["id"]} | Назва: {reader["name"]} | Ціна: {reader["price"]} | Од: {reader["unit"]} | ID Категорії: {catVal}");
                    }
                }
                menu_go(m_dbConnection);
            }
            else if (menu1 == 5)
            {
                Console.WriteLine("Завершення роботи.");
            }
            else
            {
                Console.WriteLine("Невідомий пункт меню!");
                menu_go(m_dbConnection);
            }
        }
    }
}