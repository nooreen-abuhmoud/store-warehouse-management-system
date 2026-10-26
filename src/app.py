import tkinter as tk
from tkinter import ttk, messagebox
from mysql.connector import Error
import mysql.connector
from sales import  SalesApp
import matplotlib.pyplot as plt
import db_config
# -------------------------


def safe_int(x):
    try:
        return int(x)
    except:
        return None

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Women Handbag store and its warehouse")
        self.geometry("1100x700")

        self.conn = None

    
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_category = ttk.Frame(self.nb)
        self.tab_warehouse = ttk.Frame(self.nb)
        self.tab_stock = ttk.Frame(self.nb)
        self.tab_item = ttk.Frame(self.nb)
        self.tab_supplier = ttk.Frame(self.nb)
        self.tab_supply = ttk.Frame(self.nb)
        self.tab_transfer = ttk.Frame(self.nb)
        self.tab_reports = ttk.Frame(self.nb)
        self.tab_conn = ttk.Frame(self.nb)
        self.tab_employee = ttk.Frame(self.nb)
        self.tab_customers = ttk.Frame(self.nb)
        self.tab_sales = ttk.Frame(self.nb)
        self.tab_reports_ops = ttk.Frame(self.nb)     # supply and transfer Reports 
        self.tab_reports_sales = ttk.Frame(self.nb)  #  Sales Reports
        self.tab_store_inventory = ttk.Frame(self.nb)

        
        self.nb.add(self.tab_employee, text="Employee")
        self.nb.add(self.tab_category, text="Category")
        self.nb.add(self.tab_item, text="Item")
        self.nb.add(self.tab_supplier, text="Supplier")
        self.nb.add(self.tab_supply, text="Supply Orders")
        self.nb.add(self.tab_transfer, text="Stock Transfer")

        self.nb.add(self.tab_reports_ops, text="Reports")          # warehouse reports 
        self.nb.add(self.tab_warehouse, text="Warehouse")
        self.nb.add(self.tab_stock, text="Stock")
        self.nb.add(self.tab_conn, text="Connection")

        self.nb.add(self.tab_customers, text="Customers Managment")
        self.nb.add(self.tab_store_inventory, text="Store Inventory")
        self.nb.add(self.tab_sales, text="Sales / Orders")
        self.nb.add(self.tab_reports_sales, text="Sales Reports")  # sales reports 


        self.build_connection_tab()  
        self.build_category_tab()
        self.build_item_tab()
        self.build_supplier_tab()
        self.build_supply_tab()
        self.build_transfer_tab()
        self.build_warehouse_tab()
        self.build_stock_tab()
        self.build_reports_tab() #for stock and supply and warehouse 
        self.build_employee_tab()
        self.build_store_inventory_tab()
        
        self.nb.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        self.sales_ui =  SalesApp(
            parent_app=self,
            tab_customers=self.tab_customers,
            tab_sales=self.tab_sales,
            tab_sales_reports=self.tab_reports_sales
        )
    
        self.refresh_all()
    
    def connect_db(self):
            if self.conn and self.conn.is_connected():
                return
            self.conn = mysql.connector.connect(
                host=db_config.DB_HOST,
                user=db_config.DB_USER,
                password=db_config.DB_PASSWORD,
                database=db_config.DB_NAME,
                port=db_config.DB_PORT
            )

    def run_select(self, sql, params=None):
        self.connect_db()
        cur = self.conn.cursor()
        try:
            cur.execute(sql, params or ())
            return cur.fetchall()
        finally:
            cur.close()
            
    def run_execute(self, sql, params=None):
        if not self.ensure_connection(silent=True):
            return False, "Not connected to database."

        cur = self.conn.cursor()
        try:
            cur.execute(sql, params or ())
            self.conn.commit()
            return True, ""
        except Error as e:
            self.conn.rollback()
            return False, str(e)
        finally:
            cur.close()
   
    def ensure_connection(self, silent=False):
        try:
            if not self.conn or not self.conn.is_connected():
                self.connect_db()
            return True
        except Exception as e:
            if not silent:
                messagebox.showerror("DB Error", str(e))
            return False

    # -------------------------
    # Buttons
    def test_db_connection(self):
        import db
        try:
            con = db.get_connection()
            cur = con.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
            cur.close()
            con.close()
            messagebox.showinfo("DB", "Connected successfully :)")
        except Exception as e:
            messagebox.showerror("DB", f"Connection failed :( \n{e}")  
             
    # -------------------------
    # CONNECTION TAB
    def build_connection_tab(self):
        frm = ttk.Frame(self.tab_conn, padding=12)
        frm.pack(fill="both", expand=True)

        box = ttk.LabelFrame(frm, text="Database Connection", padding=10)
        box.pack(fill="x")

        ttk.Label(box, text="Host:").grid(row=0, column=0, sticky="w", pady=3)
        self.conn_host = ttk.Entry(box, width=30)
        self.conn_host.grid(row=0, column=1, sticky="w", padx=5, pady=3)
        self.conn_host.insert(0, db_config.DB_HOST)

        ttk.Label(box, text="User:").grid(row=1, column=0, sticky="w", pady=3)
        self.conn_user = ttk.Entry(box, width=30)
        self.conn_user.grid(row=1, column=1, sticky="w", padx=5, pady=3)
        self.conn_user.insert(0, db_config.DB_USER)

        ttk.Label(box, text="Password:").grid(row=2, column=0, sticky="w", pady=3)
        self.conn_pass = ttk.Entry(box, width=30, show="*")
        self.conn_pass.grid(row=2, column=1, sticky="w", padx=5, pady=3)
        self.conn_pass.insert(0, db_config.DB_PASSWORD)

        ttk.Label(box, text="Database:").grid(row=3, column=0, sticky="w", pady=3)
        self.conn_db = ttk.Entry(box, width=30)
        self.conn_db.grid(row=3, column=1, sticky="w", padx=5, pady=3)
        self.conn_db.insert(0, db_config.DB_NAME)

        btns = ttk.Frame(box)
        btns.grid(row=0, column=2, rowspan=4, padx=10, sticky="ns")

        ttk.Button(btns, text="Connect", command=self.on_connect).pack(fill="x", pady=2)
        ttk.Button(btns, text="Disconnect", command=self.on_disconnect).pack(fill="x", pady=2)
        ttk.Button(btns, text="Test Query", command=self.on_test_query).pack(fill="x", pady=2)

        self.status = ttk.Label(frm, text="Status: Disconnected")
        self.status.pack(anchor="w", pady=10)

    def on_connect(self):
        db_config.DB_HOST = self.conn_host.get().strip()
        db_config.DB_USER = self.conn_user.get().strip()
        db_config.DB_PASSWORD = self.conn_pass.get().strip()
        db_config.DB_NAME = self.conn_db.get().strip()
        
        try:
            self.ensure_connection()
            self.status.config(text="Status: Connected ")
            messagebox.showinfo("Connection", "Connected successfully.")
            self.refresh_all()
        except Error as e:
            self.status.config(text="Status: Connection Failed ")
            messagebox.showerror("Connection failed", str(e))

    def on_disconnect(self):
        try:
            if self.conn and self.conn.is_connected():
                self.conn.close()
            self.conn = None
            self.status.config(text="Status: Disconnected")
            messagebox.showinfo("Connection", "Disconnected.")
        except Exception as e:
            messagebox.showerror("Disconnect", str(e))

    def on_test_query(self):
        if not self.conn or not self.conn.is_connected():
            messagebox.showerror("Test", "Not connected.")
            return
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT DATABASE()")
            db = cur.fetchone()[0]
            cur.close()
            messagebox.showinfo("Test Query", f"Connected to DB: {db}")
        except Error as e:
            messagebox.showerror("Test Query", str(e))

    # -------------------------
    # CATEGORY TAB
    def build_category_tab(self):
        frm = ttk.Frame(self.tab_category, padding=10)
        frm.pack(fill="both", expand=True)

        form = ttk.LabelFrame(frm, text="Category", padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Category ID (update/delete):").grid(row=0, column=0, sticky="w", pady=2)
        self.cat_id = ttk.Entry(form, width=20)
        self.cat_id.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(form, text="Category Name:").grid(row=1, column=0, sticky="w", pady=2)
        self.cat_name = ttk.Entry(form, width=40)
        self.cat_name.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        btns = ttk.Frame(form)
        btns.grid(row=0, column=2, rowspan=2, padx=10)
        ttk.Button(btns, text="Insert", command=self.category_insert).pack(fill="x", pady=2)
        ttk.Button(btns, text="Update", command=self.category_update).pack(fill="x", pady=2)
        ttk.Button(btns, text="Delete", command=self.category_delete).pack(fill="x", pady=2)
        ttk.Button(btns, text="Clear", command=self.category_clear).pack(fill="x", pady=2)

        search = ttk.Frame(frm)
        search.pack(fill="x", pady=8)
        ttk.Label(search, text="Search name contains:").pack(side="left")
        self.cat_search = ttk.Entry(search, width=40)
        self.cat_search.pack(side="left", padx=5)
        ttk.Button(search, text="Search", command=self.category_search).pack(side="left", padx=5)
        ttk.Button(search, text="Refresh", command=self.refresh_categories).pack(side="left")

        self.cat_tree = ttk.Treeview(frm, columns=("id", "name"), show="headings", height=18)
        self.cat_tree.heading("id", text="Category_ID")
        self.cat_tree.heading("name", text="Category_Name")
        self.cat_tree.column("id", width=120)
        self.cat_tree.column("name", width=700)
        self.cat_tree.pack(fill="both", expand=True)

        self.cat_tree.bind("<<TreeviewSelect>>", self.category_on_select)

    def category_on_select(self, _):
        sel = self.cat_tree.selection()
        if not sel:
            return
        cid, cname = self.cat_tree.item(sel[0], "values")
        self.cat_id.delete(0, "end"); self.cat_id.insert(0, cid)
        self.cat_name.delete(0, "end"); self.cat_name.insert(0, cname)

    def category_clear(self):
        self.cat_id.delete(0, "end")
        self.cat_name.delete(0, "end")

    def refresh_categories(self):
        for i in self.cat_tree.get_children():
            self.cat_tree.delete(i)
        rows = self.run_select("SELECT Category_ID, Category_Name FROM Category ORDER BY Category_ID")
        for r in rows:
            self.cat_tree.insert("", "end", values=r)
        self.refresh_category_dropdown()

    def category_search(self):
        term = self.cat_search.get().strip()
        for i in self.cat_tree.get_children():
            self.cat_tree.delete(i)
        rows = self.run_select(
            "SELECT Category_ID, Category_Name FROM Category WHERE Category_Name LIKE %s ORDER BY Category_ID",
            (f"%{term}%",)
        )
        for r in rows:
            self.cat_tree.insert("", "end", values=r)

    def category_insert(self):
        name = self.cat_name.get().strip()
        if not name:
            messagebox.showerror("Invalid", "Category name is required.")
            return
        ok, msg = self.run_execute("INSERT INTO Category (Category_Name) VALUES (%s)", (name,))
        if ok:
            self.refresh_categories()
            messagebox.showinfo("Done", " Category inserted.")
        else:
            messagebox.showerror("Error", msg)

    def category_update(self):
        cid = safe_int(self.cat_id.get().strip())
        name = self.cat_name.get().strip()
        if not cid or not name:
            messagebox.showerror("Invalid", "Category ID and name are required.")
            return
        ok, msg = self.run_execute("UPDATE Category SET Category_Name=%s WHERE Category_ID=%s", (name, cid))
        if ok:
            self.refresh_categories()
            messagebox.showinfo("Done", " Category updated.")
        else:
            messagebox.showerror("Error", msg)

    def category_delete(self):
        cid = safe_int(self.cat_id.get().strip())
        if not cid:
            messagebox.showerror("Invalid", "Category ID is required.")
            return
        if not messagebox.askyesno("Confirm", "Delete this category? (May fail if referenced by Item)"):
            return
        ok, msg = self.run_execute("DELETE FROM Category WHERE Category_ID=%s", (cid,))
        if ok:
            self.refresh_categories()
            messagebox.showinfo("Done", "Category deleted.")
        else:
            messagebox.showerror("Error", msg)

    # -------------------------
    # ITEM TAB
    def build_item_tab(self):
        frm = ttk.Frame(self.tab_item, padding=10)
        frm.pack(fill="both", expand=True)

        form = ttk.LabelFrame(frm, text="Item", padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Item ID (update/delete):").grid(row=0, column=0, sticky="w", pady=2)
        self.item_id = ttk.Entry(form, width=20)
        self.item_id.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(form, text="Item Name:").grid(row=1, column=0, sticky="w", pady=2)
        self.item_name = ttk.Entry(form, width=40)
        self.item_name.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(form, text="Category:").grid(row=2, column=0, sticky="w", pady=2)
        self.item_cat = ttk.Combobox(form, state="readonly", width=37)
        self.item_cat.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        btns = ttk.Frame(form)
        btns.grid(row=0, column=2, rowspan=3, padx=10)
        ttk.Button(btns, text="Insert", command=self.item_insert).pack(fill="x", pady=2)
        ttk.Button(btns, text="Update", command=self.item_update).pack(fill="x", pady=2)
        ttk.Button(btns, text="Delete", command=self.item_delete).pack(fill="x", pady=2)
        ttk.Button(btns, text="Clear", command=self.item_clear).pack(fill="x", pady=2)

        search = ttk.Frame(frm)
        search.pack(fill="x", pady=8)
        ttk.Label(search, text="Search item contains:").pack(side="left")
        self.item_search = ttk.Entry(search, width=40)
        self.item_search.pack(side="left", padx=5)
        ttk.Button(search, text="Search", command=self.item_search_run).pack(side="left", padx=5)
        ttk.Button(search, text="Refresh", command=self.refresh_items).pack(side="left")

        self.item_tree = ttk.Treeview(frm, columns=("id", "name", "cat_id", "cat_name"), show="headings", height=18)
        for col, txt, w in [
            ("id", "Item_ID", 90),
            ("name", "Item_Name", 420),
            ("cat_id", "Category_ID", 110),
            ("cat_name", "Category_Name", 260),
        ]:
            self.item_tree.heading(col, text=txt)
            self.item_tree.column(col, width=w)

        self.item_tree.pack(fill="both", expand=True)
        self.item_tree.bind("<<TreeviewSelect>>", self.item_on_select)

    def refresh_category_dropdown(self):
        rows = self.run_select("SELECT Category_ID, Category_Name FROM Category ORDER BY Category_ID")
        self.item_cat["values"] = [f"{cid} - {name}" for cid, name in rows]

    def refresh_items(self):
        for i in self.item_tree.get_children():
            self.item_tree.delete(i)
        sql = """
        SELECT i.Item_ID, i.Item_Name, c.Category_ID, c.Category_Name
        FROM Item i
        JOIN Category c ON i.Category_ID = c.Category_ID
        ORDER BY i.Item_ID
        """
        rows = self.run_select(sql)
        for r in rows:
            self.item_tree.insert("", "end", values=r)
        self.refresh_category_dropdown()

    def item_on_select(self, _):
        sel = self.item_tree.selection()
        if not sel:
            return
        iid, name, cid, cname = self.item_tree.item(sel[0], "values")
        self.item_id.delete(0, "end"); self.item_id.insert(0, iid)
        self.item_name.delete(0, "end"); self.item_name.insert(0, name)
        target = f"{cid} - {cname}"
        if target in self.item_cat["values"]:
            self.item_cat.set(target)
        else:
            self.item_cat.set("")

    def item_clear(self):
        self.item_id.delete(0, "end")
        self.item_name.delete(0, "end")
        self.item_cat.set("")

    def item_search_run(self):
        term = self.item_search.get().strip()
        for i in self.item_tree.get_children():
            self.item_tree.delete(i)
        sql = """
        SELECT i.Item_ID, i.Item_Name, c.Category_ID, c.Category_Name
        FROM Item i
        JOIN Category c ON i.Category_ID = c.Category_ID
        WHERE i.Item_Name LIKE %s
        ORDER BY i.Item_ID
        """
        rows = self.run_select(sql, (f"%{term}%",))
        for r in rows:
            self.item_tree.insert("", "end", values=r)

    def item_insert(self):
        name = self.item_name.get().strip()
        cat = self.item_cat.get().strip()
        if not name or not cat:
            messagebox.showerror("Invalid", "Item name and Category are required.")
            return
        cat_id = safe_int(cat.split(" - ")[0])
        ok, msg = self.run_execute("INSERT INTO Item (Item_Name, Category_ID) VALUES (%s,%s)", (name, cat_id))
        if ok:
            self.refresh_items()
            self.refresh_supply_dropdowns()
            self.refresh_transfer_dropdowns()

            messagebox.showinfo("Done", "Item inserted.")
        else:
            messagebox.showerror("Error", msg)

    def item_update(self):
        iid = safe_int(self.item_id.get().strip())
        name = self.item_name.get().strip()
        cat = self.item_cat.get().strip()
        if not iid or not name or not cat:
            messagebox.showerror("Invalid", "Item ID, name, and Category are required.")
            return
        cat_id = safe_int(cat.split(" - ")[0])
        ok, msg = self.run_execute(
            "UPDATE Item SET Item_Name=%s, Category_ID=%s WHERE Item_ID=%s",
            (name, cat_id, iid)
        )
        if ok:
            self.refresh_items()
            messagebox.showinfo("Done", "Item updated.")
        else:
            messagebox.showerror("Error", msg)

    def item_delete(self):
        iid = safe_int(self.item_id.get().strip())
        if not iid:
            messagebox.showerror("Invalid", "Item ID is required.")
            return
        if not messagebox.askyesno("Confirm", "Delete this item? (May fail if referenced by inventory/orders)"):
            return
        ok, msg = self.run_execute("DELETE FROM Item WHERE Item_ID=%s", (iid,))
        if ok:
            self.refresh_items()
            messagebox.showinfo("Done", "Item deleted.")
        else:
            messagebox.showerror("Error", msg)

    # -------------------------
    # SUPPLIER TAB
    def build_supplier_tab(self):
        frm = ttk.Frame(self.tab_supplier, padding=10)
        frm.pack(fill="both", expand=True)

        form = ttk.LabelFrame(frm, text="Supplier", padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Supplier ID (update/delete):").grid(row=0, column=0, sticky="w", pady=2)
        self.sup_id = ttk.Entry(form, width=20)
        self.sup_id.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(form, text="Name:").grid(row=1, column=0, sticky="w", pady=2)
        self.sup_name = ttk.Entry(form, width=40)
        self.sup_name.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(form, text="Phone:").grid(row=2, column=0, sticky="w", pady=2)
        self.sup_phone = ttk.Entry(form, width=40)
        self.sup_phone.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(form, text="Email:").grid(row=3, column=0, sticky="w", pady=2)
        self.sup_email = ttk.Entry(form, width=40)
        self.sup_email.grid(row=3, column=1, padx=5, pady=2, sticky="w")

        btns = ttk.Frame(form)
        btns.grid(row=0, column=2, rowspan=4, padx=10)
        ttk.Button(btns, text="Insert", command=self.supplier_insert).pack(fill="x", pady=2)
        ttk.Button(btns, text="Update", command=self.supplier_update).pack(fill="x", pady=2)
        ttk.Button(btns, text="Delete", command=self.supplier_delete).pack(fill="x", pady=2)
        ttk.Button(btns, text="Clear", command=self.supplier_clear).pack(fill="x", pady=2)

        search = ttk.Frame(frm)
        search.pack(fill="x", pady=8)
        ttk.Label(search, text="Search name contains:").pack(side="left")
        self.sup_search = ttk.Entry(search, width=40)
        self.sup_search.pack(side="left", padx=5)
        ttk.Button(search, text="Search", command=self.supplier_search).pack(side="left", padx=5)
        ttk.Button(search, text="Refresh", command=self.refresh_suppliers).pack(side="left")

        self.supplier_tree = ttk.Treeview(frm, columns=("id","name","phone","email"), show="headings", height=18)

        for col, txt, w in [
            ("id","Supplier_ID",100),
            ("name","Name",320),
            ("phone","Phone",200),
            ("email","Email",320),
        ]:
            self.supplier_tree.heading(col, text=txt)
            self.supplier_tree.column(col, width=w)
        self.supplier_tree.pack(fill="both", expand=True)
        self.supplier_tree.bind("<<TreeviewSelect>>", self.supplier_on_select)

    def refresh_suppliers(self):
        for i in self.supplier_tree.get_children():
            self.supplier_tree.delete(i)
        rows = self.run_select("SELECT Supplier_ID, Name, Phone, Email FROM Supplier ORDER BY Supplier_ID")
        for r in rows:
            self.supplier_tree.insert("", "end", values=r)

    def supplier_on_select(self, _):
        sel = self.supplier_tree.selection()
        if not sel:
            return
        sid, name, phone, email = self.supplier_tree.item(sel[0], "values")
        self.sup_id.delete(0,"end"); self.sup_id.insert(0, sid)
        self.sup_name.delete(0,"end"); self.sup_name.insert(0, name)
        self.sup_phone.delete(0,"end"); self.sup_phone.insert(0, phone or "")
        self.sup_email.delete(0,"end"); self.sup_email.insert(0, email or "")

    def supplier_clear(self):
        self.sup_id.delete(0,"end")
        self.sup_name.delete(0,"end")
        self.sup_phone.delete(0,"end")
        self.sup_email.delete(0,"end")

    def supplier_search(self):
        term = self.sup_search.get().strip()
        for i in self.supplier_tree.get_children():
            self.supplier_tree.delete(i)
        rows = self.run_select(
            "SELECT Supplier_ID, Name, Phone, Email FROM Supplier WHERE Name LIKE %s ORDER BY Supplier_ID",
            (f"%{term}%",)
        )
        for r in rows:
            self.supplier_tree.insert("", "end", values=r)

    def supplier_insert(self):
        name = self.sup_name.get().strip()
        if not name:
            messagebox.showerror("Invalid", "Supplier name is required.")
            return
        phone = self.sup_phone.get().strip() or None
        email = self.sup_email.get().strip() or None
        ok, msg = self.run_execute(
            "INSERT INTO Supplier (Name, Phone, Email) VALUES (%s,%s,%s)",
            (name, phone, email)
        )
        if ok:
            self.refresh_suppliers()
            self.refresh_supply_dropdowns()
            messagebox.showinfo("Done", "Supplier inserted.")
        else:
            messagebox.showerror("Error", msg)

    def supplier_update(self):
        sid = safe_int(self.sup_id.get().strip())
        name = self.sup_name.get().strip()
        if not sid or not name:
            messagebox.showerror("Invalid", "Supplier ID and name are required.")
            return
        phone = self.sup_phone.get().strip() or None
        email = self.sup_email.get().strip() or None
        ok, msg = self.run_execute(
            "UPDATE Supplier SET Name=%s, Phone=%s, Email=%s WHERE Supplier_ID=%s",
            (name, phone, email, sid)
        )
        if ok:
            self.refresh_suppliers()
            messagebox.showinfo("Done", "Supplier updated.")
        else:
            messagebox.showerror("Error", msg)

    def supplier_delete(self):
        sid = safe_int(self.sup_id.get().strip())
        if not sid:
            messagebox.showerror("Invalid", "Supplier ID is required.")
            return
        if not messagebox.askyesno("Confirm", "Delete this supplier? (May fail if referenced by Supply Orders)"):
            return
        ok, msg = self.run_execute("DELETE FROM Supplier WHERE Supplier_ID=%s", (sid,))
        if ok:
            self.refresh_suppliers()
            messagebox.showinfo("Done", " Supplier deleted.")
        else:
            messagebox.showerror("Error", msg)
    # -------------------------
    # SUPPLY TAB
    def build_supply_tab(self):
        frm = ttk.Frame(self.tab_supply, padding=10)
        frm.pack(fill="both", expand=True)

        top = ttk.LabelFrame(frm, text="New Supply Order (Warehouse fixed = 1)", padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Supplier:").grid(row=0, column=0, sticky="w")
        self.sup_supplier_cb = ttk.Combobox(top, state="readonly", width=40)
        self.sup_supplier_cb.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(top, text="Employee (warehouse staff):").grid(row=1, column=0, sticky="w")
        self.sup_employee_cb = ttk.Combobox(top, state="readonly", width=40)
        self.sup_employee_cb.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(top, text="Order Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="w")
        self.sup_date = ttk.Entry(top, width=20)
        self.sup_date.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        # Details input
        det = ttk.LabelFrame(frm, text="Add Items to Order (Details)", padding=10)
        det.pack(fill="x", pady=10)

        ttk.Label(det, text="Item:").grid(row=0, column=0, sticky="w")
        self.sup_item_cb = ttk.Combobox(det, state="readonly", width=40)
        self.sup_item_cb.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(det, text="Qty:").grid(row=0, column=2, sticky="w")
        self.sup_qty = ttk.Entry(det, width=10)
        self.sup_qty.grid(row=0, column=3, padx=5, pady=2, sticky="w")

        ttk.Label(det, text="Unit Cost:").grid(row=0, column=4, sticky="w")
        self.sup_cost = ttk.Entry(det, width=12)
        self.sup_cost.grid(row=0, column=5, padx=5, pady=2, sticky="w")

        ttk.Button(det, text="Add Line", command=self.sup_add_line).grid(row=0, column=6, padx=8)
        ttk.Button(det, text="Remove Selected Line", command=self.sup_remove_line).grid(row=0, column=7, padx=8)

        # lines table (in-memory cart)
        self.sup_lines = []
        self.sup_tree = ttk.Treeview(frm, columns=("item_id","item_name","qty","unit_cost","line_total"),
                                    show="headings", height=12)
        for col, txt, w in [
            ("item_id","Item_ID",80),
            ("item_name","Item_Name",350),
            ("qty","Qty",80),
            ("unit_cost","Unit_Cost",100),
            ("line_total","Line_Total",120),
        ]:
            self.sup_tree.heading(col, text=txt)
            self.sup_tree.column(col, width=w)
        self.sup_tree.pack(fill="both", expand=True)

        bottom = ttk.Frame(frm)
        bottom.pack(fill="x", pady=10)

        self.sup_total_lbl = ttk.Label(bottom, text="Total: 0.00")
        self.sup_total_lbl.pack(side="left")

        ttk.Button(bottom, text="POST / Save Order", command=self.sup_post_order).pack(side="right", padx=5)
        ttk.Button(bottom, text="Clear Order", command=self.sup_clear_order).pack(side="right", padx=5)

        self.refresh_supply_dropdowns()

    def refresh_supply_dropdowns(self):
        # suppliers
        sup = self.run_select("SELECT Supplier_ID, Name FROM Supplier ORDER BY Supplier_ID")
        self.sup_supplier_cb["values"] = [f"{sid} - {name}" for sid, name in sup]
        # employees (warehouse employees only)
        emp = self.run_select("""
            SELECT e.Employee_ID, e.Name
            FROM Employee e
            JOIN Warehouse_Employee we ON we.Employee_ID = e.Employee_ID
            WHERE we.Warehouse_ID = 1
            ORDER BY e.Employee_ID
        """)
        self.sup_employee_cb["values"] = [f"{eid} - {name}" for eid, name in emp]
        # items
        items = self.run_select("SELECT Item_ID, Item_Name FROM Item ORDER BY Item_ID")
        self.sup_item_cb["values"] = [f"{iid} - {name}" for iid, name in items]

    def sup_recalc_total(self):
        total = 0.0
        for line in self.sup_lines:
            total += line["qty"] * line["unit_cost"]
        self.sup_total_lbl.config(text=f"Total: {total:.2f}")

    def sup_add_line(self):
        item = self.sup_item_cb.get().strip()
        qty = safe_int(self.sup_qty.get().strip())
        try:
            cost = float(self.sup_cost.get().strip())
        except:
            cost = None

        if not item or not qty or qty <= 0 or cost is None or cost < 0:
            messagebox.showerror("Invalid", "Select Item + enter Qty (>0) + Unit Cost (>=0).")
            return

        item_id = safe_int(item.split(" - ")[0])
        item_name = " - ".join(item.split(" - ")[1:])

        self.sup_lines.append({"item_id": item_id, "item_name": item_name, "qty": qty, "unit_cost": cost})
        self.sup_tree.insert("", "end", values=(item_id, item_name, qty, f"{cost:.2f}", f"{qty*cost:.2f}"))

        self.sup_qty.delete(0, "end")
        self.sup_cost.delete(0, "end")
        self.sup_recalc_total()

    def sup_remove_line(self):
        sel = self.sup_tree.selection()
        if not sel:
            return
        idx = self.sup_tree.index(sel[0])
        self.sup_tree.delete(sel[0])
        if 0 <= idx < len(self.sup_lines):
            self.sup_lines.pop(idx)
        self.sup_recalc_total()

    def sup_clear_order(self):
        self.sup_lines = []
        for i in self.sup_tree.get_children():
            self.sup_tree.delete(i)
        self.sup_date.delete(0, "end")
        self.sup_recalc_total()

    def sup_post_order(self):
        supplier = self.sup_supplier_cb.get().strip()
        employee = self.sup_employee_cb.get().strip()
        date = self.sup_date.get().strip()

        if not supplier or not employee or not date:
            messagebox.showerror("Invalid", "Supplier + Employee + Order Date are required.")
            return
        if not self.sup_lines:
            messagebox.showerror("Invalid", "Add at least one line in details.")
            return

        supplier_id = safe_int(supplier.split(" - ")[0])
        employee_id = safe_int(employee.split(" - ")[0])
        warehouse_id = 1  # fixed

        # calculate total
        total = 0.0
        for line in self.sup_lines:
            total += line["qty"] * line["unit_cost"]

        # Transaction: insert header -> get id -> insert details -> update stock
        if not self.ensure_connection(silent=True):
            messagebox.showerror("DB", "Not connected.")
            return

        cur = self.conn.cursor()
        try:
            # header
            cur.execute("""
                INSERT INTO Supply_Order (Supplier_ID, Employee_ID, Warehouse_ID, Order_Date, Total_Amount)
                VALUES (%s,%s,%s,%s,%s)
            """, (supplier_id, employee_id, warehouse_id, date, total))
            supply_id = cur.lastrowid

            # details + stock update
            for line in self.sup_lines:
                cur.execute("""
                    INSERT INTO Supply_Order_Details (SupplyOrder_ID, Item_ID, Quantity_Purchased, Unit_Cost)
                    VALUES (%s,%s,%s,%s)
                """, (supply_id, line["item_id"], line["qty"], line["unit_cost"]))

                # upsert stock: if exists -> add, else insert
                cur.execute("""
                    INSERT INTO Stock (Warehouse_ID, Item_ID, Quantity_Warehouse)
                    VALUES (1, %s, %s)
                    ON DUPLICATE KEY UPDATE Quantity_Warehouse = Quantity_Warehouse + VALUES(Quantity_Warehouse)
                """, (line["item_id"], line["qty"]))

            self.conn.commit()
            messagebox.showinfo("Done", f"✅ Supply Order posted. ID = {supply_id}\nStock updated.")
            self.sup_clear_order()
        except Error as e:
            self.conn.rollback()
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
    # -------------------------
    # TRANSFER TAB
    def build_transfer_tab(self):
        frm = ttk.Frame(self.tab_transfer, padding=10)
        frm.pack(fill="both", expand=True)

        top = ttk.LabelFrame(frm, text="New Stock Transfer (Warehouse=1 -> Store=1 fixed)", padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Employee (warehouse staff):").grid(row=0, column=0, sticky="w")
        self.tr_emp_cb = ttk.Combobox(top, state="readonly", width=40)
        self.tr_emp_cb.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(top, text="Transfer Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w")
        self.tr_date = ttk.Entry(top, width=20)
        self.tr_date.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        det = ttk.LabelFrame(frm, text="Transfer Items", padding=10)
        det.pack(fill="x", pady=10)

        ttk.Label(det, text="Item:").grid(row=0, column=0, sticky="w")
        self.tr_item_cb = ttk.Combobox(det, state="readonly", width=40)
        self.tr_item_cb.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(det, text="Qty:").grid(row=0, column=2, sticky="w")
        self.tr_qty = ttk.Entry(det, width=10)
        self.tr_qty.grid(row=0, column=3, padx=5, pady=2, sticky="w")

        ttk.Button(det, text="Add Line", command=self.tr_add_line).grid(row=0, column=4, padx=8)
        ttk.Button(det, text="Remove Selected Line", command=self.tr_remove_line).grid(row=0, column=5, padx=8)

        self.tr_lines = []
        self.tr_tree = ttk.Treeview(frm, columns=("item_id","item_name","qty"), show="headings", height=12)
        for col, txt, w in [
            ("item_id","Item_ID",80),
            ("item_name","Item_Name",420),
            ("qty","Qty",80),
        ]:
            self.tr_tree.heading(col, text=txt)
            self.tr_tree.column(col, width=w)
        self.tr_tree.pack(fill="both", expand=True)

        bottom = ttk.Frame(frm)
        bottom.pack(fill="x", pady=10)
        ttk.Button(bottom, text="POST / Save Transfer", command=self.tr_post).pack(side="right", padx=5)
        ttk.Button(bottom, text="Clear", command=self.tr_clear).pack(side="right", padx=5)

        self.refresh_transfer_dropdowns()

    def refresh_transfer_dropdowns(self):
        emp = self.run_select("""
            SELECT e.Employee_ID, e.Name
            FROM Employee e
            JOIN Warehouse_Employee we ON we.Employee_ID = e.Employee_ID
            WHERE we.Warehouse_ID = 1
            ORDER BY e.Employee_ID
        """)
        self.tr_emp_cb["values"] = [f"{eid} - {name}" for eid, name in emp]

        items = self.run_select("SELECT Item_ID, Item_Name FROM Item ORDER BY Item_ID")
        self.tr_item_cb["values"] = [f"{iid} - {name}" for iid, name in items]

    def tr_add_line(self):
        item = self.tr_item_cb.get().strip()
        qty = safe_int(self.tr_qty.get().strip())
        if not item or not qty or qty <= 0:
            messagebox.showerror("Invalid", "Select Item + enter Qty (>0).")
            return
        item_id = safe_int(item.split(" - ")[0])
        item_name = " - ".join(item.split(" - ")[1:])
        self.tr_lines.append({"item_id": item_id, "item_name": item_name, "qty": qty})
        self.tr_tree.insert("", "end", values=(item_id, item_name, qty))
        self.tr_qty.delete(0, "end")

    def tr_remove_line(self):
        sel = self.tr_tree.selection()
        if not sel:
            return
        idx = self.tr_tree.index(sel[0])
        self.tr_tree.delete(sel[0])
        if 0 <= idx < len(self.tr_lines):
            self.tr_lines.pop(idx)

    def tr_clear(self):
        self.tr_lines = []
        for i in self.tr_tree.get_children():
            self.tr_tree.delete(i)
        self.tr_date.delete(0, "end")

    def tr_post(self):
        emp = self.tr_emp_cb.get().strip()
        date = self.tr_date.get().strip()
        if not emp or not date:
            messagebox.showerror("Invalid", "Employee + Transfer Date are required.")
            return
        if not self.tr_lines:
            messagebox.showerror("Invalid", "Add at least one line.")
            return

        employee_id = safe_int(emp.split(" - ")[0])
        warehouse_id = 1
        store_id = 1

        if not self.ensure_connection(silent=True):
            messagebox.showerror("DB", "Not connected.")
            return

        cur = self.conn.cursor()
        try:
            # Validate stock availability first
            for line in self.tr_lines:
                cur.execute("""
                    SELECT Quantity_Warehouse FROM Stock
                    WHERE Warehouse_ID=1 AND Item_ID=%s
                """, (line["item_id"],))
                row = cur.fetchone()
                have = row[0] if row else 0
                if have < line["qty"]:
                    raise Exception(f"Not enough stock for Item_ID={line['item_id']} (have {have}, need {line['qty']})")

            # header
            cur.execute("""
                INSERT INTO Stock_Transfer (Warehouse_ID, Store_ID, Employee_ID, Transfer_Date)
                VALUES (%s,%s,%s,%s)
            """, (warehouse_id, store_id, employee_id, date))
            transfer_id = cur.lastrowid

            # details + update stock/store_inventory
            for line in self.tr_lines:
                cur.execute("""
                    INSERT INTO StockTransfer_Detail (Transfer_ID, Item_ID, Quantity_Transferred)
                    VALUES (%s,%s,%s)
                """, (transfer_id, line["item_id"], line["qty"]))

                # decrease warehouse stock
                cur.execute("""
                    UPDATE Stock
                    SET Quantity_Warehouse = Quantity_Warehouse - %s
                    WHERE Warehouse_ID=1 AND Item_ID=%s
                """, (line["qty"], line["item_id"]))

                # upsert store inventory (price stays as is if exists)
                cur.execute("""
                    INSERT INTO Store_Inventory (Store_ID, Item_ID, Selling_Price, Quantity_Store)
                    VALUES (1, %s, 0.00, %s)
                    ON DUPLICATE KEY UPDATE Quantity_Store = Quantity_Store + VALUES(Quantity_Store)
                """, (line["item_id"], line["qty"]))

            self.conn.commit()
            messagebox.showinfo("Done", f"✅ Transfer posted. ID = {transfer_id}\nWarehouse stock decreased, store inventory increased.")
            self.tr_clear()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
    # -------------------------
    # WAREHOUSE TAB (ONLY UPDATE capacity/location, no insert/delete)
    def build_warehouse_tab(self):
        frm = ttk.Frame(self.tab_warehouse, padding=10)
        frm.pack(fill="both", expand=True)

        box = ttk.LabelFrame(frm, text="Warehouse (Fixed: ID = 1)", padding=10)
        box.pack(fill="x")

        ttk.Label(box, text="Warehouse ID:").grid(row=0, column=0, sticky="w", pady=3)
        self.wh_id_lbl = ttk.Label(box, text="1")
        self.wh_id_lbl.grid(row=0, column=1, sticky="w", pady=3)

        ttk.Label(box, text="Location:").grid(row=1, column=0, sticky="w", pady=3)
        self.wh_location = ttk.Entry(box, width=50)
        self.wh_location.grid(row=1, column=1, padx=5, pady=3, sticky="w")

        ttk.Label(box, text="Capacity:").grid(row=2, column=0, sticky="w", pady=3)
        self.wh_capacity = ttk.Entry(box, width=20)
        self.wh_capacity.grid(row=2, column=1, padx=5, pady=3, sticky="w")

        btns = ttk.Frame(box)
        btns.grid(row=0, column=2, rowspan=3, padx=10, sticky="ns")

        ttk.Button(btns, text="Load", command=self.wh_load).pack(fill="x", pady=2)
        ttk.Button(btns, text="Update", command=self.wh_update).pack(fill="x", pady=2)

        note = ttk.Label(frm, text="Note: No insert/delete here. Only update the existing warehouse (ID=1).")
        note.pack(anchor="w", pady=8)

        # load on open
        self.wh_load()

    def wh_load(self):
        if not self.ensure_connection(silent=True):
            return
        row = self.run_select("SELECT Location, Capacity FROM Warehouse WHERE Warehouse_ID=1")
        loc, cap = row[0]
        self.wh_location.delete(0, "end"); self.wh_location.insert(0, loc or "")
        self.wh_capacity.delete(0, "end"); self.wh_capacity.insert(0, str(cap))

    def wh_update(self):
        loc = self.wh_location.get().strip()
        cap = safe_int(self.wh_capacity.get().strip())

        if cap is None or cap < 0:
            messagebox.showerror("Invalid", "Capacity must be a non-negative integer.")
            return
        if not loc:
            messagebox.showerror("Invalid", "Location is required.")
            return

        ok, msg = self.run_execute(
            "UPDATE Warehouse SET Location=%s, Capacity=%s WHERE Warehouse_ID=1",
            (loc, cap)
        )
        if ok:
            messagebox.showinfo("Done", "Warehouse updated successfully.")
        else:
            messagebox.showerror("Error", msg)
        # -------------------------
    # REPORTS TAB
    def build_reports_tab(self):
        frm = ttk.Frame(self.tab_reports_ops, padding=10)
        frm.pack(fill="both", expand=True)

        controls = ttk.LabelFrame(frm, text="Reports Controls", padding=10)
        controls.pack(fill="x")

        ttk.Label(controls, text="From (YYYY-MM-DD):").grid(row=0, column=0, sticky="w")
        self.rep_from = ttk.Entry(controls, width=15)
        self.rep_from.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(controls, text="To (YYYY-MM-DD):").grid(row=0, column=2, sticky="w")
        self.rep_to = ttk.Entry(controls, width=15)
        self.rep_to.grid(row=0, column=3, padx=5, pady=2, sticky="w")

        ttk.Label(controls, text="Low Stock Threshold:").grid(row=0, column=4, sticky="w")
        self.rep_threshold = ttk.Entry(controls, width=10)
        self.rep_threshold.grid(row=0, column=5, padx=5, pady=2, sticky="w")
        self.rep_threshold.insert(0, "50")

        btns = ttk.Frame(frm)
        btns.pack(fill="x", pady=8)

        ttk.Button(btns, text="1) Total Supply Purchases:", command=self.rep_total_supply).pack(side="left", padx=5)
        ttk.Button(btns, text="2) Top Purchased Items:", command=self.rep_top_items).pack(side="left", padx=5)
        ttk.Button(btns, text="3) Warehouse Stock (Now)", command=self.rep_wh_stock).pack(side="left", padx=5)
        ttk.Button(btns, text="4) Low Stock Alert", command=self.rep_low_stock).pack(side="left", padx=5)
        ttk.Button(btns, text="5) Warehouse Load (Capacity vs Current Stock)", command=self.rep_wh_load).pack(side="left", padx=5)

        self.rep_tree = ttk.Treeview(frm, show="headings", height=18)
        self.rep_tree.pack(fill="both", expand=True)
                # track last report (for chart)
        self._last_report = None
        self._last_report_rows = []
        self._last_report_cols = []

        ttk.Button(btns, text=" Show Chart", command=self.rep_show_chart).pack(side="left", padx=12)


    def rep_total_supply(self):
        d1 = self.rep_from.get().strip()
        d2 = self.rep_to.get().strip()
        if not d1 or not d2:
            messagebox.showerror("Invalid", "Enter From and To dates.")
            return
        rows = self.run_select("""
            SELECT COUNT(*) AS Orders_Count, SUM(Total_Amount) AS Total_Purchased
            FROM Supply_Order
            WHERE Order_Date BETWEEN %s AND %s
        """, (d1, d2))
        
        self._last_report = "total_supply"
        self.rep_set_table(["Orders_Count", "Total_Purchased"], rows)

    def rep_top_items(self):
        d1 = self.rep_from.get().strip()
        d2 = self.rep_to.get().strip()
        if not d1 or not d2:
            messagebox.showerror("Invalid", "Enter From and To dates.")
            return
        rows = self.run_select("""
            SELECT d.Item_ID, i.Item_Name,
                SUM(d.Quantity_Purchased) AS Total_Qty,
                ROUND(SUM(d.Quantity_Purchased * d.Unit_Cost), 2) AS Total_Cost
            FROM Supply_Order_Details d
            JOIN Supply_Order h ON h.SupplyOrder_ID = d.SupplyOrder_ID
            JOIN Item i ON i.Item_ID = d.Item_ID
            WHERE h.Order_Date BETWEEN %s AND %s
            GROUP BY d.Item_ID, i.Item_Name
            ORDER BY Total_Qty DESC
            LIMIT 10
        """, (d1, d2))
        self._last_report = "top_items"
        self.rep_set_table(["Item_ID","Item_Name","Total_Qty","Total_Cost"], rows)

    def rep_wh_stock(self):
        rows = self.run_select("""
            SELECT s.Item_ID, i.Item_Name, s.Quantity_Warehouse
            FROM Stock s
            JOIN Item i ON i.Item_ID = s.Item_ID
            WHERE s.Warehouse_ID = 1
            ORDER BY s.Quantity_Warehouse DESC
        """)
        self.rep_set_table(["Item_ID","Item_Name","Quantity_Warehouse"], rows)

    def rep_low_stock(self):
        th = safe_int(self.rep_threshold.get().strip())
        if th is None or th < 0:
            messagebox.showerror("Invalid", "Threshold must be a non-negative integer.")
            return
        rows = self.run_select("""
            SELECT s.Item_ID, i.Item_Name, s.Quantity_Warehouse
            FROM Stock s
            JOIN Item i ON i.Item_ID = s.Item_ID
            WHERE s.Warehouse_ID = 1 AND s.Quantity_Warehouse < %s
            ORDER BY s.Quantity_Warehouse ASC
        """, (th,))
        self._last_report = "low_stock"
        self.rep_set_table(["Item_ID","Item_Name","Quantity_Warehouse"], rows)

    def rep_wh_load(self):
        rows = self.run_select("""
            SELECT 
                w.Capacity AS Capacity,
                SUM(s.Quantity_Warehouse) AS Current_Load,
                (w.Capacity - SUM(s.Quantity_Warehouse)) AS Remaining
            FROM Warehouse w
            LEFT JOIN Stock s ON s.Warehouse_ID = w.Warehouse_ID
            WHERE w.Warehouse_ID = 1
            GROUP BY w.Warehouse_ID, w.Capacity
        """)
        self._last_report = "wh_load"
        self.rep_set_table(["Capacity", "Current_Load", "Remaining"], rows)
        
        
    
    def rep_show_chart(self):
        if not getattr(self, "_last_report", None):
            messagebox.showerror("Chart", "Run a report first, then click Show Chart.")
            return

        rows = getattr(self, "_last_report_rows", None) or []
        if not rows:
            messagebox.showinfo("Chart", "No data to plot.")
            return

        rpt = self._last_report

        try:
            # 1) Total Supply Purchases (single row)
            if rpt == "total_supply":
                orders_count, total_purchased = rows[0]
                orders_count = 0 if orders_count is None else int(orders_count)
                total_purchased = 0 if total_purchased is None else float(total_purchased)

                plt.figure()
                plt.title("Total Supply Purchases (Period)")
                plt.bar(["Orders", "Total Purchased"], [orders_count, total_purchased])
                plt.ylabel("Value")
                plt.show()
                return

            # 2) Top Purchased Items
            if rpt == "top_items":
                # rows: (Item_ID, Item_Name, Total_Qty, Total_Cost)
                names = [r[1] for r in rows]
                qtys = [float(r[2]) for r in rows]

                plt.figure()
                plt.title("Top Purchased Items (Total Qty)")
                plt.bar(names, qtys)
                plt.ylabel("Total Qty")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                plt.show()
                return

            # 3) Warehouse Stock (Now)
            if rpt == "wh_stock":
                # rows: (Item_ID, Item_Name, Quantity_Warehouse)
                # show top 10 only (already ordered desc)
                top = rows[:10]
                names = [r[1] for r in top]
                qtys = [float(r[2]) for r in top]

                plt.figure()
                plt.title("Warehouse Stock (Top 10 by Quantity)")
                plt.bar(names, qtys)
                plt.ylabel("Quantity")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                plt.show()
                return

            # 4) Low Stock Alert
            if rpt == "low_stock":
                # rows: (Item_ID, Item_Name, Quantity_Warehouse)
                names = [r[1] for r in rows]
                qtys = [float(r[2]) for r in rows]

                plt.figure()
                plt.title("Low Stock Alert")
                plt.bar(names, qtys)
                plt.ylabel("Quantity (Warehouse)")
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                plt.show()
                return

            # 5) Warehouse Load (pie)
            if rpt == "wh_load":
                cap, cur_load, remaining = rows[0]
                cap = 0 if cap is None else float(cap)
                cur_load = 0 if cur_load is None else float(cur_load)
                remaining = 0 if remaining is None else float(remaining)

                # sometimes remaining can be None if no stock rows exist
                if cap > 0 and remaining == 0 and cur_load == 0:
                    # still OK
                    pass

                used = cur_load
                free = remaining if remaining is not None else max(cap - used, 0)

                plt.figure()
                plt.title("Warehouse Load")
                plt.pie([used, free], labels=["Current Load", "Remaining"], autopct="%1.1f%%")
                plt.show()
                return

            messagebox.showinfo("Chart", "This report has no chart mapping yet.")

        except Exception as e:
            messagebox.showerror("Chart Error", str(e))
    
    def rep_set_table(self, columns, rows):
                # store last result for charts
                self._last_report_cols = columns
                self._last_report_rows = rows

                self.rep_tree.delete(*self.rep_tree.get_children())
                self.rep_tree["columns"] = columns
                for c in columns:
                    self.rep_tree.heading(c, text=c)
                    self.rep_tree.column(c, width=180)
                for r in rows:
                    self.rep_tree.insert("", "end", values=r)

            
        # -------------------------
        # stock 
    def build_stock_tab(self):
        frm = ttk.Frame(self.tab_stock, padding=10)
        frm.pack(fill="both", expand=True)

        top = ttk.LabelFrame(frm, text="Warehouse Stock (Fixed Warehouse_ID = 1)", padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Item:").grid(row=0, column=0, sticky="w", pady=3)
        self.stock_item_cb = ttk.Combobox(top, state="readonly", width=45)
        self.stock_item_cb.grid(row=0, column=1, padx=5, pady=3, sticky="w")

        ttk.Label(top, text="Quantity:").grid(row=0, column=2, sticky="w", pady=3)
        self.stock_qty = ttk.Entry(top, width=12)
        self.stock_qty.grid(row=0, column=3, padx=5, pady=3, sticky="w")

        btns = ttk.Frame(top)
        btns.grid(row=0, column=4, padx=10, sticky="w")

        ttk.Button(btns, text="Set Quantity", command=self.stock_set_qty).pack(side="left", padx=4)
        ttk.Button(btns, text="Add Qty", command=self.stock_add_qty).pack(side="left", padx=4)
        ttk.Button(btns, text="Subtract Qty", command=self.stock_subtract_qty).pack(side="left", padx=4)
        ttk.Button(btns, text="Delete Row", command=self.stock_delete_row).pack(side="left", padx=4)
        ttk.Button(btns, text="Refresh", command=self.refresh_stock).pack(side="left", padx=4)

        self.stock_info = ttk.Label(frm, text="Tip: Stock is for Warehouse_ID=1 only.")
        self.stock_info.pack(anchor="w", pady=8)

        self.stock_tree = ttk.Treeview(frm, columns=("item_id","item_name","qty"), show="headings", height=18)
        self.stock_tree.heading("item_id", text="Item_ID")
        self.stock_tree.heading("item_name", text="Item_Name")
        self.stock_tree.heading("qty", text="Quantity_Warehouse")

        self.stock_tree.column("item_id", width=90)
        self.stock_tree.column("item_name", width=560)
        self.stock_tree.column("qty", width=160)

        self.stock_tree.pack(fill="both", expand=True)
        self.stock_tree.bind("<<TreeviewSelect>>", self.stock_on_select)

        # load initial
        self.refresh_stock_dropdown()
        self.refresh_stock()


    def refresh_stock_dropdown(self):
        rows = self.run_select("SELECT Item_ID, Item_Name FROM Item ORDER BY Item_ID")
        self.stock_item_cb["values"] = [f"{iid} - {name}" for iid, name in rows]


    def refresh_stock(self):
        # refresh combobox too (if items changed)
        self.refresh_stock_dropdown()

        for i in self.stock_tree.get_children():
            self.stock_tree.delete(i)

        rows = self.run_select("""
            SELECT s.Item_ID, i.Item_Name, s.Quantity_Warehouse
            FROM Stock s
            JOIN Item i ON i.Item_ID = s.Item_ID
            WHERE s.Warehouse_ID = 1
            ORDER BY s.Item_ID
        """)
        for r in rows:
            self.stock_tree.insert("", "end", values=r)


    def stock_on_select(self, _):
        sel = self.stock_tree.selection()
        if not sel:
            return
        item_id, item_name, qty = self.stock_tree.item(sel[0], "values")
        target = f"{item_id} - {item_name}"
        if target in self.stock_item_cb["values"]:
            self.stock_item_cb.set(target)
        self.stock_qty.delete(0, "end")
        self.stock_qty.insert(0, str(qty))


    def _stock_get_inputs(self):
        item = self.stock_item_cb.get().strip()
        qty = safe_int(self.stock_qty.get().strip())
        if not item:
            return None, None, "Select an Item."
        item_id = safe_int(item.split(" - ")[0])
        if item_id is None:
            return None, None, "Invalid Item."
        if qty is None or qty < 0:
            return None, None, "Quantity must be a non-negative integer."
        return item_id, qty, None


    def stock_set_qty(self):
        item_id, qty, err = self._stock_get_inputs()
        if err:
            messagebox.showerror("Invalid", err)
            return

        # Upsert: set exact quantity
        ok, msg = self.run_execute("""
            INSERT INTO Stock (Warehouse_ID, Item_ID, Quantity_Warehouse)
            VALUES (1, %s, %s)
            ON DUPLICATE KEY UPDATE Quantity_Warehouse = VALUES(Quantity_Warehouse)
        """, (item_id, qty))

        if ok:
            messagebox.showinfo("Done", "Stock quantity set successfully.")
            self.refresh_stock()
        else:
            messagebox.showerror("Error", msg)


    def stock_add_qty(self):
        item_id, qty, err = self._stock_get_inputs()
        if err:
            messagebox.showerror("Invalid", err)
            return
        if qty == 0:
            messagebox.showerror("Invalid", "Enter quantity > 0 to add.")
            return

        ok, msg = self.run_execute("""
            INSERT INTO Stock (Warehouse_ID, Item_ID, Quantity_Warehouse)
            VALUES (1, %s, %s)
            ON DUPLICATE KEY UPDATE Quantity_Warehouse = Quantity_Warehouse + VALUES(Quantity_Warehouse)
        """, (item_id, qty))

        if ok:
            messagebox.showinfo("Done", "Stock increased successfully.")
            self.refresh_stock()
        else:
            messagebox.showerror("Error", msg)


    def stock_subtract_qty(self):
        item = self.stock_item_cb.get().strip()
        dec = safe_int(self.stock_qty.get().strip())

        if not item:
            messagebox.showerror("Invalid", "Select an Item.")
            return
        if dec is None or dec <= 0:
            messagebox.showerror("Invalid", "Enter quantity > 0 to subtract.")
            return

        item_id = safe_int(item.split(" - ")[0])

        # check current
        row = self.run_select("""
            SELECT Quantity_Warehouse
            FROM Stock
            WHERE Warehouse_ID=1 AND Item_ID=%s
        """, (item_id,))

        current = row[0][0] if row else 0
        if current < dec:
            messagebox.showerror("Invalid", f"Not enough stock. Have {current}, need {dec}.")
            return

        ok, msg = self.run_execute("""
            UPDATE Stock
            SET Quantity_Warehouse = Quantity_Warehouse - %s
            WHERE Warehouse_ID=1 AND Item_ID=%s
        """, (dec, item_id))

        if ok:
            messagebox.showinfo("Done", "Stock decreased successfully.")
            self.refresh_stock()
        else:
            messagebox.showerror("Error", msg)


    def stock_delete_row(self):
        item = self.stock_item_cb.get().strip()
        if not item:
            messagebox.showerror("Invalid", "Select an Item first.")
            return
        item_id = safe_int(item.split(" - ")[0])

        if not messagebox.askyesno("Confirm", "Delete this Stock row for Warehouse_ID=1?"):
            return

        ok, msg = self.run_execute("""
            DELETE FROM Stock
            WHERE Warehouse_ID=1 AND Item_ID=%s
        """, (item_id,))

        if ok:
            messagebox.showinfo("Done", "Stock row deleted.")
            self.stock_qty.delete(0, "end")
            self.refresh_stock()
        else:
            messagebox.showerror("Error", msg)
    # -------------------------
    # EMPLOYEE TAB (Master + Assign to Store/Warehouse, exclusive)
    def build_employee_tab(self):
        frm = ttk.Frame(self.tab_employee, padding=10)
        frm.pack(fill="both", expand=True)

        form = ttk.LabelFrame(frm, text="Employee", padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Employee ID (update/delete):").grid(row=0, column=0, sticky="w", pady=2)
        self.emp_id = ttk.Entry(form, width=20)
        self.emp_id.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(form, text="Name:").grid(row=1, column=0, sticky="w", pady=2)
        self.emp_name = ttk.Entry(form, width=40)
        self.emp_name.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(form, text="Role:").grid(row=2, column=0, sticky="w", pady=2)
        self.emp_role = ttk.Entry(form, width=40)
        self.emp_role.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        btns = ttk.Frame(form)
        btns.grid(row=0, column=2, rowspan=3, padx=10)
        ttk.Button(btns, text="Insert", command=self.emp_insert).pack(fill="x", pady=2)
        ttk.Button(btns, text="Update", command=self.emp_update).pack(fill="x", pady=2)
        ttk.Button(btns, text="Delete", command=self.emp_delete).pack(fill="x", pady=2)
        ttk.Button(btns, text="Clear", command=self.emp_clear).pack(fill="x", pady=2)

        assign = ttk.LabelFrame(frm, text="Assign (exclusive: Store OR Warehouse)", padding=10)
        assign.pack(fill="x", pady=10)

        ttk.Label(assign, text="Assign selected Employee to:").grid(row=0, column=0, sticky="w")

        ttk.Button(assign, text="Assign to Store (Store_ID=1)", command=self.emp_assign_store).grid(row=0, column=1, padx=6)
        ttk.Button(assign, text="Assign to Warehouse (Warehouse_ID=1)", command=self.emp_assign_warehouse).grid(row=0, column=2, padx=6)
        ttk.Button(assign, text="Remove Assignment", command=self.emp_remove_assignment).grid(row=0, column=3, padx=6)

        self.emp_assign_status = ttk.Label(assign, text="Assignment: -")
        self.emp_assign_status.grid(row=0, column=4, padx=10, sticky="w")

        search = ttk.Frame(frm)
        search.pack(fill="x", pady=8)
        ttk.Label(search, text="Search name contains:").pack(side="left")
        self.emp_search = ttk.Entry(search, width=40)
        self.emp_search.pack(side="left", padx=5)
        ttk.Button(search, text="Search", command=self.emp_search_run).pack(side="left", padx=5)
        ttk.Button(search, text="Refresh", command=self.refresh_employees).pack(side="left")

        self.emp_tree = ttk.Treeview(frm, columns=("id","name","role","assignment"), show="headings", height=18)
        for col, txt, w in [
            ("id","Employee_ID",100),
            ("name","Name",280),
            ("role","Role",200),
            ("assignment","Assignment",200),
        ]:
            self.emp_tree.heading(col, text=txt)
            self.emp_tree.column(col, width=w)
        self.emp_tree.pack(fill="both", expand=True)
        self.emp_tree.bind("<<TreeviewSelect>>", self.emp_on_select)

        self.refresh_employees()

    def emp_clear(self):
        self.emp_id.delete(0,"end")
        self.emp_name.delete(0,"end")
        self.emp_role.delete(0,"end")
        self.emp_assign_status.config(text="Assignment: -")

    def emp_on_select(self, _):
        sel = self.emp_tree.selection()
        if not sel:
            return
        eid, name, role, assignment = self.emp_tree.item(sel[0], "values")
        self.emp_id.delete(0,"end"); self.emp_id.insert(0, eid)
        self.emp_name.delete(0,"end"); self.emp_name.insert(0, name)
        self.emp_role.delete(0,"end"); self.emp_role.insert(0, role or "")
        self.emp_assign_status.config(text=f"Assignment: {assignment}")

    def refresh_employees(self):
        for i in self.emp_tree.get_children():
            self.emp_tree.delete(i)

        rows = self.run_select("""
            SELECT e.Employee_ID, e.Name, e.Role,
            CASE
                WHEN se.Employee_ID IS NOT NULL THEN 'STORE'
                WHEN we.Employee_ID IS NOT NULL THEN 'WAREHOUSE'
                ELSE 'UNASSIGNED'
            END AS Assignment
            FROM Employee e
            LEFT JOIN Store_Employee se ON se.Employee_ID = e.Employee_ID
            LEFT JOIN Warehouse_Employee we ON we.Employee_ID = e.Employee_ID
            ORDER BY e.Employee_ID
        """)

        for r in rows:
            self.emp_tree.insert("", "end", values=r)

    def emp_search_run(self):
        term = self.emp_search.get().strip()
        for i in self.emp_tree.get_children():
            self.emp_tree.delete(i)
        rows = self.run_select("""
            SELECT e.Employee_ID, e.Name, e.Role,
            CASE
                WHEN se.Employee_ID IS NOT NULL THEN 'STORE'
                WHEN we.Employee_ID IS NOT NULL THEN 'WAREHOUSE'
                ELSE 'UNASSIGNED'
            END AS Assignment
            FROM Employee e
            LEFT JOIN Store_Employee se ON se.Employee_ID = e.Employee_ID
            LEFT JOIN Warehouse_Employee we ON we.Employee_ID = e.Employee_ID
            WHERE e.Name LIKE %s
            ORDER BY e.Employee_ID
        """, (f"%{term}%",))
        for r in rows:
            self.emp_tree.insert("", "end", values=r)

    def emp_insert(self):
        name = self.emp_name.get().strip()
        role = self.emp_role.get().strip() or None
        if not name:
            messagebox.showerror("Invalid", "Employee name is required.")
            return
        ok, msg = self.run_execute("INSERT INTO Employee (Name, Role) VALUES (%s,%s)", (name, role))
        if ok:
            self.refresh_employees()
            # refresh dropdowns that depend on warehouse employees:
            self.refresh_supply_dropdowns()
            self.refresh_transfer_dropdowns()
            self.sales_ui.refresh_sales_dropdowns()
            messagebox.showinfo("Done", "Employee inserted.")
        else:
            messagebox.showerror("Error", msg)

    def emp_update(self):
        eid = safe_int(self.emp_id.get().strip())
        name = self.emp_name.get().strip()
        role = self.emp_role.get().strip() or None
        if not eid or not name:
            messagebox.showerror("Invalid", "Employee ID and name are required.")
            return
        ok, msg = self.run_execute("UPDATE Employee SET Name=%s, Role=%s WHERE Employee_ID=%s", (name, role, eid))
        if ok:
            self.refresh_employees()
            self.refresh_supply_dropdowns()
            self.refresh_transfer_dropdowns()
            self.sales_ui.refresh_sales_dropdowns()
            messagebox.showinfo("Done", "Employee updated.")
        else:
            messagebox.showerror("Error", msg)

    def emp_delete(self):
        eid = safe_int(self.emp_id.get().strip())
        if not eid:
            messagebox.showerror("Invalid", "Employee ID is required.")
            return
        if not messagebox.askyesno("Confirm", "Delete this employee?"):
            return
        ok, msg = self.run_execute("DELETE FROM Employee WHERE Employee_ID=%s", (eid,))
        if ok:
            self.refresh_employees()
            self.refresh_supply_dropdowns()
            self.refresh_transfer_dropdowns()
            self.sales_ui.refresh_sales_dropdowns()
            messagebox.showinfo("Done", "Employee deleted.")
        else:
            messagebox.showerror("Error", msg)

    def emp_assign_store(self):
        eid = safe_int(self.emp_id.get().strip())
        if not eid:
            messagebox.showerror("Invalid", "Select an employee first.")
            return

        # If already in warehouse -> block
        in_wh = self.run_select("SELECT 1 FROM Warehouse_Employee WHERE Employee_ID=%s", (eid,))
        if in_wh:
            messagebox.showerror("Not allowed", "This employee is already assigned to WAREHOUSE. Remove assignment first.")
            return

        ok, msg = self.run_execute("INSERT INTO Store_Employee (Employee_ID, Store_ID) VALUES (%s, 1)", (eid,))
        if ok:
            self.refresh_employees()
            self.sales_ui.refresh_sales_dropdowns()
            messagebox.showinfo("Done", "Assigned to STORE (Store_ID=1).")
        else:
            messagebox.showerror("Error", msg)

    def emp_assign_warehouse(self):
        eid = safe_int(self.emp_id.get().strip())
        if not eid:
            messagebox.showerror("Invalid", "Select an employee first.")
            return

        # If already in store -> block
        in_store = self.run_select("SELECT 1 FROM Store_Employee WHERE Employee_ID=%s", (eid,))
        if in_store:
            messagebox.showerror("Not allowed", "This employee is already assigned to STORE. Remove assignment first.")
            return

        ok, msg = self.run_execute("INSERT INTO Warehouse_Employee (Employee_ID, Warehouse_ID) VALUES (%s, 1)", (eid,))
        if ok:
            self.refresh_employees()
            self.refresh_supply_dropdowns()
            self.refresh_transfer_dropdowns()
            self.sales_ui.refresh_sales_dropdowns()
            messagebox.showinfo("Done", "Assigned to WAREHOUSE (Warehouse_ID=1).")
        else:
            messagebox.showerror("Error", msg)

    def emp_remove_assignment(self):
        eid = safe_int(self.emp_id.get().strip())
        if not eid:
            messagebox.showerror("Invalid", "Select an employee first.")
            return

        # Remove from both (only one should exist)
        ok1, msg1 = self.run_execute("DELETE FROM Store_Employee WHERE Employee_ID=%s", (eid,))
        ok2, msg2 = self.run_execute("DELETE FROM Warehouse_Employee WHERE Employee_ID=%s", (eid,))

        if ok1 and ok2:
            self.refresh_employees()
            self.refresh_supply_dropdowns()
            self.refresh_transfer_dropdowns()
            messagebox.showinfo("Done", "Assignment removed (if existed).")
        else:
            messagebox.showerror("Error", f"{msg1}\n{msg2}")
            
    def build_store_inventory_tab(self):
        frm = ttk.Frame(self.tab_store_inventory, padding=10)
        frm.pack(fill="both", expand=True)

        top = ttk.LabelFrame(frm, text="Store Inventory (Fixed Store_ID = 1)", padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Item:").grid(row=0, column=0, sticky="w", pady=3)
        self.si_item_cb = ttk.Combobox(top, state="readonly", width=45)
        self.si_item_cb.grid(row=0, column=1, padx=5, pady=3, sticky="w")

        ttk.Label(top, text="Selling Price:").grid(row=0, column=2, sticky="w", pady=3)
        self.si_price = ttk.Entry(top, width=12)
        self.si_price.grid(row=0, column=3, padx=5, pady=3, sticky="w")

        ttk.Label(top, text="Quantity:").grid(row=0, column=4, sticky="w", pady=3)
        self.si_qty = ttk.Entry(top, width=12)
        self.si_qty.grid(row=0, column=5, padx=5, pady=3, sticky="w")

        btns = ttk.Frame(top)
        btns.grid(row=0, column=6, padx=10, sticky="w")

        ttk.Button(btns, text="Upsert (Set)", command=self.si_upsert_set).pack(side="left", padx=4)
        ttk.Button(btns, text="Add Qty", command=self.si_add_qty).pack(side="left", padx=4)
        ttk.Button(btns, text="Subtract Qty", command=self.si_subtract_qty).pack(side="left", padx=4)
        ttk.Button(btns, text="Delete Row", command=self.si_delete_row).pack(side="left", padx=4)
        ttk.Button(btns, text="Refresh", command=self.refresh_store_inventory).pack(side="left", padx=4)

        self.si_tree = ttk.Treeview(frm, columns=("item_id", "item_name", "price", "qty"), show="headings", height=18)
        self.si_tree.heading("item_id", text="Item_ID")
        self.si_tree.heading("item_name", text="Item_Name")
        self.si_tree.heading("price", text="Selling_Price")
        self.si_tree.heading("qty", text="Quantity_Store")

        self.si_tree.column("item_id", width=90)
        self.si_tree.column("item_name", width=520)
        self.si_tree.column("price", width=140)
        self.si_tree.column("qty", width=140)

        self.si_tree.pack(fill="both", expand=True)
        self.si_tree.bind("<<TreeviewSelect>>", self.si_on_select)

        self.refresh_store_inventory_dropdown()
        self.refresh_store_inventory()


    def refresh_store_inventory_dropdown(self):
        rows = self.run_select("SELECT Item_ID, Item_Name FROM Item ORDER BY Item_ID")
        self.si_item_cb["values"] = [f"{iid} - {name}" for iid, name in rows]


    def refresh_store_inventory(self):
        self.refresh_store_inventory_dropdown()

        for i in self.si_tree.get_children():
            self.si_tree.delete(i)

        rows = self.run_select("""
            SELECT si.Item_ID, i.Item_Name, si.Selling_Price, si.Quantity_Store
            FROM Store_Inventory si
            JOIN Item i ON i.Item_ID = si.Item_ID
            WHERE si.Store_ID = 1
            ORDER BY i.Item_ID
        """)
        for r in rows:
            self.si_tree.insert("", "end", values=r)

        # كمان نحدّث sales dropdowns عشان يظهر أي تعديل فوراً
        try:
            self.sales_ui.refresh_sales_dropdowns()
        except:
            pass


    def si_on_select(self, _):
        sel = self.si_tree.selection()
        if not sel:
            return
        item_id, item_name, price, qty = self.si_tree.item(sel[0], "values")
        target = f"{item_id} - {item_name}"
        if target in self.si_item_cb["values"]:
            self.si_item_cb.set(target)
        self.si_price.delete(0, "end")
        self.si_price.insert(0, str(price))
        self.si_qty.delete(0, "end")
        self.si_qty.insert(0, str(qty))


    def _si_get_inputs(self):
        item = self.si_item_cb.get().strip()
        if not item:
            return None, None, None, "Select an Item."

        item_id = safe_int(item.split(" - ")[0])
        if item_id is None:
            return None, None, None, "Invalid Item."

        # price
        try:
            price = float(self.si_price.get().strip())
        except:
            return None, None, None, "Selling price must be a number."

        qty = safe_int(self.si_qty.get().strip())
        if qty is None or qty < 0:
            return None, None, None, "Quantity must be a non-negative integer."

        if price < 0:
            return None, None, None, "Selling price must be >= 0."

        return item_id, price, qty, None


    def si_upsert_set(self):
        item_id, price, qty, err = self._si_get_inputs()
        if err:
            messagebox.showerror("Invalid", err)
            return

        ok, msg = self.run_execute("""
            INSERT INTO Store_Inventory (Store_ID, Item_ID, Selling_Price, Quantity_Store)
            VALUES (1, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                Selling_Price = VALUES(Selling_Price),
                Quantity_Store = VALUES(Quantity_Store)
        """, (item_id, price, qty))

        if ok:
            messagebox.showinfo("Done", "Store inventory updated.")
            self.refresh_store_inventory()
        else:
            messagebox.showerror("Error", msg)


    def si_add_qty(self):
        item_id, price, qty, err = self._si_get_inputs()
        if err:
            messagebox.showerror("Invalid", err)
            return
        if qty <= 0:
            messagebox.showerror("Invalid", "Enter quantity > 0 to add.")
            return

        ok, msg = self.run_execute("""
            INSERT INTO Store_Inventory (Store_ID, Item_ID, Selling_Price, Quantity_Store)
            VALUES (1, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                Selling_Price = VALUES(Selling_Price),
                Quantity_Store = Quantity_Store + VALUES(Quantity_Store)
        """, (item_id, price, qty))

        if ok:
            messagebox.showinfo("Done", "Quantity increased.")
            self.refresh_store_inventory()
        else:
            messagebox.showerror("Error", msg)


    def si_subtract_qty(self):
        item = self.si_item_cb.get().strip()
        dec = safe_int(self.si_qty.get().strip())
        if not item:
            messagebox.showerror("Invalid", "Select an Item.")
            return
        if dec is None or dec <= 0:
            messagebox.showerror("Invalid", "Enter quantity > 0 to subtract.")
            return

        item_id = safe_int(item.split(" - ")[0])

        row = self.run_select("""
            SELECT Quantity_Store
            FROM Store_Inventory
            WHERE Store_ID=1 AND Item_ID=%s
        """, (item_id,))
        current = row[0][0] if row else 0

        if current < dec:
            messagebox.showerror("Invalid", f"Not enough quantity in store. Have {current}, need {dec}.")
            return

        ok, msg = self.run_execute("""
            UPDATE Store_Inventory
            SET Quantity_Store = Quantity_Store - %s
            WHERE Store_ID=1 AND Item_ID=%s
        """, (dec, item_id))

        if ok:
            messagebox.showinfo("Done", "Quantity decreased.")
            self.refresh_store_inventory()
        else:
            messagebox.showerror("Error", msg)


    def si_delete_row(self):
        item = self.si_item_cb.get().strip()
        if not item:
            messagebox.showerror("Invalid", "Select an Item first.")
            return
        item_id = safe_int(item.split(" - ")[0])

        if not messagebox.askyesno("Confirm", "Delete this item from Store_Inventory (Store_ID=1)?"):
            return

        ok, msg = self.run_execute("""
            DELETE FROM Store_Inventory
            WHERE Store_ID=1 AND Item_ID=%s
        """, (item_id,))

        if ok:
            messagebox.showinfo("Done", "Row deleted.")
            self.si_price.delete(0, "end")
            self.si_qty.delete(0, "end")
            self.refresh_store_inventory()
        else:
            messagebox.showerror("Error", msg)
        
#----------------------------------------------------
    def on_tab_changed(self, event):
        tab_text = event.widget.tab(event.widget.select(), "text")

        if tab_text == "Supply Orders":
            self.refresh_supply_dropdowns()
        elif tab_text == "Stock Transfer":
            self.refresh_transfer_dropdowns()
        elif tab_text == "Stock":
            self.refresh_stock()   # stock tab
        elif tab_text == "Sales / Orders":
            self.sales_ui.refresh_sales_dropdowns()
        elif tab_text == "Sales Reports":
            self.sales_ui.refresh_sales_dropdowns()
        elif tab_text == "warehouse - supply order Reports":
            pass

    def refresh_all(self):
        try:
            self.refresh_categories()
            self.refresh_items()
            self.refresh_suppliers()
            self.sales_ui.refresh_sales_dropdowns()
            # fill comboboxes (Supply + Transfer)
            self.refresh_supply_dropdowns()
            self.refresh_transfer_dropdowns()
            self.refresh_stock()
        except:
            pass

if __name__ == "__main__":
    App().mainloop()

