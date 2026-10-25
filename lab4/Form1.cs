using System;
using System.Data;
using System.IO;
using System.Windows.Forms;
using System.Xml;
using System.Globalization;

namespace lab4
{
    public partial class Form1 : Form
    {
        private DataSet storeDataSet;
        private DataTable productTable;

        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            storeDataSet = new DataSet("StoreDB");
            productTable = new DataTable("Product");

            productTable.Columns.Add(new DataColumn("DepartmentId", typeof(int)));
            productTable.Columns.Add(new DataColumn("ProductId", typeof(int)));
            productTable.Columns.Add(new DataColumn("ProductCode", typeof(string)));
            productTable.Columns.Add(new DataColumn("ProductName", typeof(string)));
            productTable.Columns.Add(new DataColumn("Price", typeof(decimal)));
            productTable.Columns.Add(new DataColumn("Description", typeof(string)));

            productTable.Rows.Add(2, 1, "HL1020", "Notebook A5", 45.00m, "Grid paper, 96 sheets");
            productTable.Rows.Add(2, 2, "HL2045", "Gel Pen Blue", 25.00m, "0.5mm quick dry ink");
            productTable.Rows.Add(2, 3, "HL9876", "Pen", 15.00m, "Quality Material: ballpoint pen");
            productTable.Rows.Add(2, 4, "HL7374", "Set of markers", 200.00m, "Includes 16 dual-tip markers");
            productTable.Rows.Add(2, 5, "HL5512", "Highlighter Set", 120.00m, "Neon colors, pack of 6");
            productTable.Rows.Add(1, 6, "EL3341", "Wireless Mouse", 350.00m, "Ergonomic 2.4GHz optical");
            productTable.Rows.Add(1, 7, "EL9901", "USB Flash Drive 64GB", 220.00m, "USB 3.0 high speed transfer");
            productTable.Rows.Add(1, 8, "EL4412", "Mechanical Keyboard", 1450.00m, "RGB backlight, blue switches");
            productTable.Rows.Add(3, 9, "OF7789", "Desk Organizer", 180.00m, "Mesh metal multi-compartment");
            productTable.Rows.Add(3, 10, "OF6611", "Paper Clips Box", 30.00m, "100 pcs colored vinyl-coated");

            storeDataSet.Tables.Add(productTable);
            dataGridView1.DataSource = storeDataSet.Tables["Product"];
        }
        
        private void button2_Click(object sender, EventArgs e)
        {
            try
            {
                DataSet ds = new DataSet();
                DataTable dtCopy = productTable.Copy();
                dtCopy.TableName = "Table";
                ds.Tables.Add(dtCopy);

                ds.WriteXml("Products.xml");
                MessageBox.Show("Готово!!!");
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.ToString());
            }
        }

        private void button3_Click(object sender, EventArgs e)
        {
            if (File.Exists("Products.xml"))
            {
                using (XmlReader xmlFile = XmlReader.Create("Products.xml", new XmlReaderSettings()))
                {
                    DataSet ds = new DataSet();
                    ds.ReadXml(xmlFile);

                    DataView dv = new DataView(ds.Tables[0], "Convert(Price, 'System.Decimal') > 100", "ProductName", DataViewRowState.CurrentRows);
                    dv.ToTable().WriteXml("Result.xml");
                }
                MessageBox.Show("Готово!!!");
            }
            else
            {
                MessageBox.Show("Файл Products.xml відсутній! Спершу створіть його.");
            }
        }

        private void button4_Click(object sender, EventArgs e)
        {
            if (File.Exists("Products.xml"))
            {
                DataSet ds = new DataSet();
                using (XmlReader xmlFile = XmlReader.Create("Products.xml", new XmlReaderSettings()))
                {
                    ds.ReadXml(xmlFile);
                }

                DataView dv = new DataView(ds.Tables[0]);
                dv.Sort = "ProductName";

                string search_name = name_of_product.Text.Trim();
                int index = dv.Find(search_name);

                if (index == -1)
                {
                    MessageBox.Show("Даний товар відсутній!!!");
                }
                else
                {
                    MessageBox.Show(
                        "Товар: " + dv[index]["ProductName"].ToString() + "\n" +
                        "Код: " + dv[index]["ProductCode"].ToString() + "\n" +
                        "Ціна: " + dv[index]["Price"].ToString() + " грн\n" +
                        "Опис: " + dv[index]["Description"].ToString()
                    );
                }
            }
            else
            {
                MessageBox.Show("Файл Products.xml відсутній! Спершу натисніть 'Створити XML на основі БД'.");
            }
        }

        private void button5_Click(object sender, EventArgs e)
        {
            if (File.Exists("Result.xml"))
            {
                DataSet ds = new DataSet();
                using (XmlReader xmlFile = XmlReader.Create("Result.xml", new XmlReaderSettings()))
                {
                    ds.ReadXml(xmlFile);
                }

                string dept = pos.Text.Trim();
                string search = "DepartmentId = " + (string.IsNullOrEmpty(dept) ? "2" : dept);
                DataView dv = new DataView(ds.Tables[0], search, "ProductName", DataViewRowState.CurrentRows);
                dv.ToTable().WriteXml("Result2.xml");

                MessageBox.Show("Готово!!!");
            }
            else
            {
                MessageBox.Show("Файл Result.xml відсутній! Спершу виконайте вибірку за ціною.");
            }
        }

        private void button6_Click(object sender, EventArgs e)
        {
            string fileName = "Products.xml";

            if (File.Exists(fileName))
            {
                DataSet ds = new DataSet();
                using (XmlReader xmlFile = XmlReader.Create(fileName, new XmlReaderSettings()))
                {
                    ds.ReadXml(xmlFile);
                }

                if (ds.Tables.Count > 0 && ds.Tables[0].Rows.Count > 0)
                {
                    productTable.Rows.Clear();

                    for (int i = 0; i < ds.Tables[0].Rows.Count; i++)
                    {
                        int deptId = Convert.ToInt32(ds.Tables[0].Rows[i]["DepartmentId"]);
                        int prodId = Convert.ToInt32(ds.Tables[0].Rows[i]["ProductId"]);
                        string code = ds.Tables[0].Rows[i]["ProductCode"].ToString();
                        string name = ds.Tables[0].Rows[i]["ProductName"].ToString();

                        string rawPrice = ds.Tables[0].Rows[i]["Price"].ToString().Trim().Replace(',', '.');
                        decimal price = decimal.Parse(rawPrice, CultureInfo.InvariantCulture);

                        string desc = ds.Tables[0].Rows[i]["Description"].ToString();

                        productTable.Rows.Add(deptId, prodId, code, name, price, desc);
                    }

                    MessageBox.Show("Готово !!! Дані з Products.xml успішно завантажено в таблицю !");
                }
                else
                {
                    MessageBox.Show("Файл Products.xml порожній або не містить таблиць!");
                }
            }
            else
            {
                MessageBox.Show("Файл Products.xml відсутній! Спершу натисніть 'Створити XML на основі БД'.");
            }
        }

        private void button7_Click(object sender, EventArgs e)
        {
            productTable.AcceptChanges();
            MessageBox.Show("Зміни збережено!");
        }

        private void button8_Click(object sender, EventArgs e)
        {
            productTable.RejectChanges();
        }

        private void button9_Click(object sender, EventArgs e)
        {
            dataGridView1.Refresh();
        }
    }
}