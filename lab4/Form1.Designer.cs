namespace lab4
{
    partial class Form1
    {
        private System.ComponentModel.IContainer components = null;
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        private void InitializeComponent()
        {
            this.button2 = new System.Windows.Forms.Button();
            this.button3 = new System.Windows.Forms.Button();
            this.button4 = new System.Windows.Forms.Button();
            this.button5 = new System.Windows.Forms.Button();
            this.button6 = new System.Windows.Forms.Button();
            this.button7 = new System.Windows.Forms.Button();
            this.button8 = new System.Windows.Forms.Button();
            this.button9 = new System.Windows.Forms.Button();
            this.name_of_product = new System.Windows.Forms.TextBox();
            this.pos = new System.Windows.Forms.TextBox();
            this.dataGridView1 = new System.Windows.Forms.DataGridView();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).BeginInit();
            this.SuspendLayout();
           
            this.button2.Location = new System.Drawing.Point(210, 20);
            this.button2.Name = "button2";
            this.button2.Size = new System.Drawing.Size(180, 45);
            this.button2.TabIndex = 1;
            this.button2.Text = "Створити XML на основі БД";
            this.button2.UseVisualStyleBackColor = true;
            this.button2.Click += new System.EventHandler(this.button2_Click);
 
            this.button3.Location = new System.Drawing.Point(400, 20);
            this.button3.Name = "button3";
            this.button3.Size = new System.Drawing.Size(180, 45);
            this.button3.TabIndex = 2;
            this.button3.Text = "Вибірка у інший XML за кодом";
            this.button3.UseVisualStyleBackColor = true;
            this.button3.Click += new System.EventHandler(this.button3_Click);
 
            this.button4.Location = new System.Drawing.Point(590, 20);
            this.button4.Name = "button4";
            this.button4.Size = new System.Drawing.Size(180, 45);
            this.button4.TabIndex = 3;
            this.button4.Text = "Пошук товару у XML файлі";
            this.button4.UseVisualStyleBackColor = true;
            this.button4.Click += new System.EventHandler(this.button4_Click);

            this.button5.Location = new System.Drawing.Point(780, 20);
            this.button5.Name = "button5";
            this.button5.Size = new System.Drawing.Size(180, 45);
            this.button5.TabIndex = 4;
            this.button5.Text = "Вибірка за відділом";
            this.button5.UseVisualStyleBackColor = true;
            this.button5.Click += new System.EventHandler(this.button5_Click);

            this.button6.Location = new System.Drawing.Point(810, 210);
            this.button6.Name = "button6";
            this.button6.Size = new System.Drawing.Size(150, 60);
            this.button6.TabIndex = 5;
            this.button6.Text = "Запис з XML до БД";
            this.button6.UseVisualStyleBackColor = true;
            this.button6.Click += new System.EventHandler(this.button6_Click);
 
            this.button7.Location = new System.Drawing.Point(20, 120);
            this.button7.Name = "button7";
            this.button7.Size = new System.Drawing.Size(110, 35);
            this.button7.TabIndex = 6;
            this.button7.Text = "Зберегти";
            this.button7.UseVisualStyleBackColor = true;
            this.button7.Click += new System.EventHandler(this.button7_Click);
  
            this.button8.Location = new System.Drawing.Point(20, 165);
            this.button8.Name = "button8";
            this.button8.Size = new System.Drawing.Size(110, 35);
            this.button8.TabIndex = 7;
            this.button8.Text = "Відхилити";
            this.button8.UseVisualStyleBackColor = true;
            this.button8.Click += new System.EventHandler(this.button8_Click);

            this.button9.Location = new System.Drawing.Point(20, 210);
            this.button9.Name = "button9";
            this.button9.Size = new System.Drawing.Size(110, 35);
            this.button9.TabIndex = 8;
            this.button9.Text = "Оновити";
            this.button9.UseVisualStyleBackColor = true;
            this.button9.Click += new System.EventHandler(this.button9_Click);

            this.name_of_product.Location = new System.Drawing.Point(590, 72);
            this.name_of_product.Name = "name_of_product";
            this.name_of_product.Size = new System.Drawing.Size(180, 22);
            this.name_of_product.TabIndex = 9;

            this.pos.Location = new System.Drawing.Point(780, 72);
            this.pos.Name = "pos";
            this.pos.Size = new System.Drawing.Size(180, 22);
            this.pos.TabIndex = 10;
 
            this.dataGridView1.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridView1.Location = new System.Drawing.Point(145, 115);
            this.dataGridView1.Name = "dataGridView1";
            this.dataGridView1.RowHeadersWidth = 51;
            this.dataGridView1.RowTemplate.Height = 24;
            this.dataGridView1.Size = new System.Drawing.Size(650, 320);
            this.dataGridView1.TabIndex = 11;

            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.None;
            this.ClientSize = new System.Drawing.Size(984, 461);
            this.Controls.Add(this.dataGridView1);
            this.Controls.Add(this.pos);
            this.Controls.Add(this.name_of_product);
            this.Controls.Add(this.button9);
            this.Controls.Add(this.button8);
            this.Controls.Add(this.button7);
            this.Controls.Add(this.button6);
            this.Controls.Add(this.button5);
            this.Controls.Add(this.button4);
            this.Controls.Add(this.button3);
            this.Controls.Add(this.button2);
            this.Name = "Form1";
            this.Text = "Lab_4_Member";
            this.Load += new System.EventHandler(this.Form1_Load);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridView1)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion
        private System.Windows.Forms.Button button2;
        private System.Windows.Forms.Button button3;
        private System.Windows.Forms.Button button4;
        private System.Windows.Forms.Button button5;
        private System.Windows.Forms.Button button6;
        private System.Windows.Forms.Button button7;
        private System.Windows.Forms.Button button8;
        private System.Windows.Forms.Button button9;
        private System.Windows.Forms.TextBox name_of_product;
        private System.Windows.Forms.TextBox pos;
        private System.Windows.Forms.DataGridView dataGridView1;
    }
}