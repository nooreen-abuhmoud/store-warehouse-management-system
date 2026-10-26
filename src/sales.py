# handbag_sales.py
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from tkinter import ttk, messagebox
from datetime import date
import db


def safe_int(s: str):
    s = s.strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def safe_float(s: str):
    s = s.strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def money(x):
    try:
        return f"{float(x):.2f}"
    except Exception:
        return "0.00"


class SalesApp:
    def __init__(self, parent_app, tab_customers, tab_sales, tab_sales_reports):
        self.app = parent_app

        self.tab_customers = tab_customers
        self.tab_sales = tab_sales
        self.tab_reports = tab_sales_reports

        self.build_customers_tab()
        self.build_sales_tab()
        self.build_reports_tab()

        self.refresh_customers_table()
        self.refresh_sales_dropdowns()
        self._last_report_type = None
        self._last_cols = None
        self._last_rows = None

    # TAB 1: Customers Managment
    # =========================================================
    def build_customers_tab(self):
        frm = ttk.LabelFrame(self.tab_customers, text="Customer Management")
        frm.pack(fill="x", padx=10, pady=10)

        ttk.Label(frm, text="Customer_ID (Update/Delete/Search):").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.c_id = tk.StringVar()
        ttk.Entry(frm, textvariable=self.c_id, width=20).grid(row=0, column=1, padx=6, pady=4, sticky="w")

        ttk.Label(frm, text="Name:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.c_name = tk.StringVar()
        ttk.Entry(frm, textvariable=self.c_name, width=35).grid(row=1, column=1, padx=6, pady=4, sticky="w")

        ttk.Label(frm, text="Phone:").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.c_phone = tk.StringVar()
        ttk.Entry(frm, textvariable=self.c_phone, width=20).grid(row=2, column=1, padx=6, pady=4, sticky="w")

        ttk.Label(frm, text="Address:").grid(row=3, column=0, sticky="w", padx=6, pady=4)
        self.c_address = tk.StringVar()
        ttk.Entry(frm, textvariable=self.c_address, width=35).grid(row=3, column=1, padx=6, pady=4, sticky="w")

        ttk.Label(frm, text="Name keyword (search):").grid(row=4, column=0, sticky="w", padx=6, pady=4)
        self.c_keyword = tk.StringVar()
        ttk.Entry(frm, textvariable=self.c_keyword, width=20).grid(row=4, column=1, padx=6, pady=4, sticky="w")

        btns = ttk.Frame(frm)
        btns.grid(row=0, column=2, rowspan=5, padx=12, pady=4, sticky="ns")

        ttk.Button(btns, text="Insert", command=self.insert_customer).pack(fill="x", pady=2)
        ttk.Button(btns, text="Update", command=self.update_customer).pack(fill="x", pady=2)
        ttk.Button(btns, text="Delete", command=self.delete_customer).pack(fill="x", pady=2)
        ttk.Button(btns, text="Search by ID", command=self.search_customer_by_id).pack(fill="x", pady=2)
        ttk.Button(btns, text="Search by Name", command=self.search_customer_by_name).pack(fill="x", pady=2)
        ttk.Button(btns, text="Clear", command=self.clear_customer_fields).pack(fill="x", pady=2)
        ttk.Button(btns, text="Refresh", command=self.refresh_customers_table).pack(fill="x", pady=2)

        table_frame = ttk.Frame(self.tab_customers)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.customer_table = ttk.Treeview(table_frame, columns=("id", "name", "phone", "address"), show="headings")
        self.customer_table.heading("id", text="Customer_ID")
        self.customer_table.heading("name", text="Name")
        self.customer_table.heading("phone", text="Phone")
        self.customer_table.heading("address", text="Address")
        self.customer_table.column("id", width=120)
        self.customer_table.column("name", width=350)
        self.customer_table.column("phone", width=200)
        self.customer_table.column("address", width=300)
        self.customer_table.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.customer_table.yview)
        self.customer_table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        self.customer_table.bind("<<TreeviewSelect>>", self.on_customer_row_select)

    def on_customer_row_select(self, event):
        sel = self.customer_table.selection()
        if not sel:
            return
        cid, name, phone, address = self.customer_table.item(sel[0], "values")
        self.c_id.set(cid)
        self.c_name.set(name)
        self.c_phone.set(phone)
        self.c_address.set(address)

    def clear_customer_fields(self):
        self.c_id.set("")
        self.c_name.set("")
        self.c_phone.set("")
        self.c_address.set("")
        self.c_keyword.set("")
        self.customer_table.selection_remove(self.customer_table.selection())

    def refresh_customers_table(self):
        for r in self.customer_table.get_children():
            self.customer_table.delete(r)

        for cid, name, phone, address in db.customer_get_all():
            self.customer_table.insert("", "end", values=(cid, name, phone, address))

        self.refresh_sales_customers()

    def insert_customer(self):
        name = self.c_name.get().strip()
        phone = self.c_phone.get().strip()
        address = self.c_address.get().strip()
        if not name or not phone:
            messagebox.showerror("Error", "Name and Phone are required.")
            return
        new_id = db.customer_insert(name, phone, address)
        messagebox.showinfo("Done", f"Inserted customer. ID = {new_id}")
        self.refresh_customers_table()
        self.clear_customer_fields()

    def update_customer(self):
        cid = safe_int(self.c_id.get())
        name = self.c_name.get().strip()
        phone = self.c_phone.get().strip()
        address = self.c_address.get().strip()
        if cid is None:
            messagebox.showerror("Error", "Enter valid Customer_ID.")
            return
        if not name or not phone:
            messagebox.showerror("Error", "Name and Phone are required.")
            return
        affected = db.customer_update(cid, name, phone, address)
        if affected == 0:
            messagebox.showwarning("Not Found", f"No customer with ID {cid}.")
        else:
            messagebox.showinfo("Done", "Customer updated.")
        self.refresh_customers_table()

    def delete_customer(self):
        cid = safe_int(self.c_id.get())
        if cid is None:
            messagebox.showerror("Error", "Enter valid Customer_ID.")
            return
        if not messagebox.askyesno("Confirm", f"Delete customer ID {cid}?"):
            return
        affected = db.customer_delete(cid)
        if affected == 0:
            messagebox.showwarning("Not Found", f"No customer with ID {cid}.")
        else:
            messagebox.showinfo("Done", "Customer deleted.")
        self.refresh_customers_table()
        self.clear_customer_fields()

    def search_customer_by_id(self):
        cid = safe_int(self.c_id.get())
        if cid is None:
            messagebox.showerror("Error", "Enter valid Customer_ID.")
            return
        row = db.customer_get_by_id(cid)
        if not row:
            messagebox.showinfo("Not Found", f"No customer with ID {cid}.")
            return
        self.c_id.set(row[0])
        self.c_name.set(row[1])
        self.c_phone.set(row[2])
        self.c_address.set(row[3])

    def search_customer_by_name(self):
        kw = self.c_keyword.get().strip()
        if not kw:
            messagebox.showerror("Error", "Enter a name keyword.")
            return
        for r in self.customer_table.get_children():
            self.customer_table.delete(r)
        rows = db.customer_search_by_name(kw)
        for cid, name, phone, address in rows:
            self.customer_table.insert("", "end", values=(cid, name, phone, address))
        if not rows:
            messagebox.showinfo("No Results", "No customers match this name.")

    # =========================================================
    # TAB 2: Sales / Orders
    # =========================================================
    def build_sales_tab(self):
        top = ttk.LabelFrame(self.tab_sales, text="Create Customer Order (Store + Auto Transfer from Warehouse)")
        top.pack(fill="x", padx=10, pady=10)

        ttk.Label(top, text="Store:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.store_var = tk.StringVar()
        self.store_cb = ttk.Combobox(top, textvariable=self.store_var, state="readonly", width=40)
        self.store_cb.grid(row=0, column=1, padx=6, pady=4, sticky="w")
        self.store_cb.bind("<<ComboboxSelected>>", lambda e: self.on_store_changed())

        ttk.Label(top, text="Employee (Store Staff):").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.emp_var = tk.StringVar()
        self.emp_cb = ttk.Combobox(top, textvariable=self.emp_var, state="readonly", width=40)
        self.emp_cb.grid(row=1, column=1, padx=6, pady=4, sticky="w")

        ttk.Label(top, text="Customer:").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.sale_customer_var = tk.StringVar()
        self.sale_customer_cb = ttk.Combobox(top, textvariable=self.sale_customer_var, state="readonly", width=40)
        self.sale_customer_cb.grid(row=2, column=1, padx=6, pady=4, sticky="w")

        ttk.Label(top, text="Product (from Store Inventory):").grid(row=3, column=0, sticky="w", padx=6, pady=4)
        self.item_var = tk.StringVar()
        self.item_cb = ttk.Combobox(top, textvariable=self.item_var, state="readonly", width=40)
        self.item_cb.grid(row=3, column=1, padx=6, pady=4, sticky="w")
        self.item_cb.bind("<<ComboboxSelected>>", lambda e: self.on_item_changed())

        ttk.Label(top, text="Unit Price:").grid(row=4, column=0, sticky="w", padx=6, pady=4)
        self.unit_price_var = tk.StringVar(value="0.00")
        ttk.Entry(top, textvariable=self.unit_price_var, width=12, state="readonly").grid(row=4, column=1, padx=6,
                                                                                          pady=4, sticky="w")
        ttk.Label(top, text="Store Qty (current):").grid(row=4, column=1, padx=140, pady=4, sticky="w")
        self.available_var = tk.StringVar(value="0")
        ttk.Entry(top, textvariable=self.available_var, width=8, state="readonly").grid(row=4, column=1, padx=260,
                                                                                        pady=4, sticky="w")

        ttk.Label(top, text="Quantity to buy:").grid(row=5, column=0, sticky="w", padx=6, pady=4)
        self.qty_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.qty_var, width=12).grid(row=5, column=1, padx=6, pady=4, sticky="w")

        ttk.Button(top, text="Add To Cart", command=self.add_to_cart).grid(row=5, column=2, padx=10, pady=4)

        ttk.Label(top, text="Order ID (to cancel):").grid(row=6, column=0, sticky="w", padx=6, pady=4)

        self.order_id_var = tk.StringVar()

        self.order_id_cb = ttk.Combobox(top, textvariable=self.order_id_var, state="readonly", width=40)
        self.order_id_cb.grid(row=6, column=1, padx=6, pady=4, sticky="w")

        self.refresh_sales_orders()

        ttk.Button(top, text="Cancel Order", command=self.cancel_order).grid(row=7, column=1, padx=10, pady=4)

        mid = ttk.LabelFrame(self.tab_sales, text="Cart (Order Details)")
        mid.pack(fill="both", expand=True, padx=10, pady=10)

        self.cart_table = ttk.Treeview(mid, columns=("item_id", "item_name", "qty", "unit", "line"), show="headings")
        for col, title, w in [
            ("item_id", "Item_ID", 90),
            ("item_name", "Item_Name", 360),
            ("qty", "Quantity", 120),
            ("unit", "Unit_Price", 120),
            ("line", "Line_Total", 120),
        ]:
            self.cart_table.heading(col, text=title)
            self.cart_table.column(col, width=w)
        self.cart_table.pack(fill="both", expand=True, padx=6, pady=6)

        bottom = ttk.Frame(self.tab_sales)
        bottom.pack(fill="x", padx=10, pady=10)

        ttk.Button(bottom, text="Remove Selected", command=self.remove_cart_selected).pack(side="left")
        ttk.Button(bottom, text="Clear Cart", command=self.clear_cart).pack(side="left", padx=8)

        self.total_lbl = ttk.Label(bottom, text="Total Amount: 0.00", font=("Arial", 12, "bold"))
        self.total_lbl.pack(side="right")

        ttk.Button(self.tab_sales, text="Create Order (Save to DB)", command=self.create_order).pack(pady=8)

    def refresh_sales_orders(self):
        orders = db.get_all_orders()
        if orders:
            order_values = [f"{order_id} - {customer_name} - {order_date}" for order_id, customer_name, order_date in
                            orders]

            self.order_id_cb["values"] = order_values

            self.order_id_cb.current(0)
        else:
            self.order_id_cb["values"] = []
            self.order_id_var.set('')

    def cancel_order(self):
        selected_order = self.order_id_var.get()

        if not selected_order:
            messagebox.showerror("Error", "Please select a valid Order ID to cancel.")
            return

        try:
            order_id = int(selected_order.split(" - ")[0].strip())
        except ValueError:
            messagebox.showerror("Error", "Invalid Order ID format. Please select a valid order.")
            return

        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to cancel Order ID {order_id}?")
        if not confirm:
            return

        store_id = self.get_selected_store_id()

        try:
            db.cancel_customer_order(order_id, store_id)
            messagebox.showinfo("Success", f"Order ID {order_id} has been successfully canceled.")

            self.refresh_sales_orders()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to cancel order: {str(e)}")

    def refresh_sales_dropdowns(self):
        self.refresh_stores()
        self.refresh_sales_customers()
        self.on_store_changed()

    def refresh_stores(self):
        stores = db.store_get_all()
        self._stores = stores
        values = [f"{sid} - {name}" for sid, name in stores]
        self.store_cb["values"] = values
        if values:
            self.store_cb.current(0)

    def refresh_sales_customers(self):
        customers = db.customer_get_all()
        self._customers = customers
        values = [f"{cid} - {name}" for cid, name, phone, address in customers]
        self.sale_customer_cb["values"] = values
        if values:
            self.sale_customer_cb.current(0)

    def get_selected_store_id(self):
        s = self.store_var.get()
        if not s:
            return None
        return int(s.split("-")[0].strip())

    def get_selected_employee_id(self):
        s = self.emp_var.get()
        if not s:
            return None
        return int(s.split("-")[0].strip())

    def get_selected_customer_id(self):
        s = self.sale_customer_var.get()
        if not s:
            return None
        return int(s.split("-")[0].strip())

    def get_selected_item_id(self):
        s = self.item_var.get()
        if not s:
            return None
        return int(s.split("-")[0].strip())

    def on_store_changed(self):
        store_id = self.get_selected_store_id()
        if store_id is None:
            return

        employees = db.employee_get_store_staff(store_id)
        self._employees = employees
        emp_values = [f"{eid} - {name} ({role})" for eid, name, role in employees]
        self.emp_cb["values"] = emp_values
        if emp_values:
            self.emp_cb.current(0)
        else:
            self.emp_var.set("")

        self._inventory_rows = db.inventory_items_for_store(store_id)
        item_values = [f"{iid} - {iname}" for iid, iname, price, qty in self._inventory_rows]
        self.item_cb["values"] = item_values
        if item_values:
            self.item_cb.current(0)
            self.on_item_changed()
        else:
            self.item_var.set("")
            self.unit_price_var.set("0.00")
            self.available_var.set("0")

    def on_item_changed(self):
        item_id = self.get_selected_item_id()
        if item_id is None:
            self.unit_price_var.set("0.00")
            self.available_var.set("0")
            return

        for iid, iname, price, qty in self._inventory_rows:
            if int(iid) == int(item_id):
                self.unit_price_var.set(money(price))
                self.available_var.set(str(qty))
                return

        self.unit_price_var.set("0.00")
        self.available_var.set("0")

    def add_to_cart(self):
        store_id = self.get_selected_store_id()
        emp_id = self.get_selected_employee_id()
        cust_id = self.get_selected_customer_id()
        item_id = self.get_selected_item_id()

        if store_id is None:
            messagebox.showerror("Error", "Select a store.")
            return
        if emp_id is None:
            messagebox.showerror("Error", "Select an employee (store staff).")
            return
        if cust_id is None:
            messagebox.showerror("Error", "Select a customer.")
            return
        if item_id is None:
            messagebox.showerror("Error", "Select a product from inventory.")
            return

        qty = safe_int(self.qty_var.get())
        if qty is None or qty <= 0:
            messagebox.showerror("Error", "Enter a valid quantity (> 0).")
            return

        store_available = safe_int(self.available_var.get()) or 0

        item_name = ""
        unit_price = 0.0
        for iid, iname, price, q in self._inventory_rows:
            if int(iid) == int(item_id):
                item_name = iname
                unit_price = float(price)
                break

        for row in self.cart_table.get_children():
            vals = self.cart_table.item(row, "values")
            if int(vals[0]) == int(item_id):
                old_qty = int(vals[2])
                new_qty = old_qty + qty
                line_total = new_qty * unit_price
                self.cart_table.item(row, values=(item_id, item_name, new_qty, money(unit_price), money(line_total)))
                self.update_total()
                self.qty_var.set("")

                if new_qty > store_available:
                    messagebox.showinfo(
                        "Notice",
                        f"Requested quantity ({new_qty}) is more than store stock ({store_available}).\n"
                        f"The system will try to transfer the shortage from warehouse when you click 'Create Order'."
                    )
                return

        line_total = qty * unit_price
        self.cart_table.insert("", "end", values=(item_id, item_name, qty, money(unit_price), money(line_total)))
        self.update_total()
        self.qty_var.set("")

        if qty > store_available:
            messagebox.showinfo(
                "Notice",
                f"Requested quantity ({qty}) is more than store stock ({store_available}).\n"
                f"The system will try to transfer the shortage from warehouse when you click 'Create Order'."
            )

    def remove_cart_selected(self):
        sel = self.cart_table.selection()
        if not sel:
            return
        for r in sel:
            self.cart_table.delete(r)
        self.update_total()

    def clear_cart(self):
        for r in self.cart_table.get_children():
            self.cart_table.delete(r)
        self.update_total()

    def update_total(self):
        total = 0.0
        for r in self.cart_table.get_children():
            vals = self.cart_table.item(r, "values")
            total += float(vals[4])
        self.total_lbl.config(text=f"Total Amount: {money(total)}")

    def create_order(self):
        store_id = self.get_selected_store_id()
        emp_id = self.get_selected_employee_id()
        cust_id = self.get_selected_customer_id()

        if store_id is None:
            messagebox.showerror("Error", "Store is required for the order.")
            return
        if emp_id is None:
            messagebox.showerror("Error", "Employee is required for the order.")
            return
        if cust_id is None:
            messagebox.showerror("Error", "Customer is required for the order.")
            return

        rows = self.cart_table.get_children()
        if not rows:
            messagebox.showerror("Error", "Cart is empty.")
            return

        cart_lines = []
        for r in rows:
            item_id, item_name, qty, unit, line = self.cart_table.item(r, "values")
            cart_lines.append({
                "item_id": int(item_id),
                "qty": int(qty),
                "unit_price": float(unit)
            })

        try:
            order_id = db.create_customer_order(
                store_id=store_id,
                employee_id=emp_id,
                customer_id=cust_id,
                order_date=date.today(),
                cart_lines=cart_lines
            )
        except Exception as e:
            messagebox.showerror("Order Failed", f"Error: {str(e)}")
            return

        messagebox.showinfo("Done", f"Order created successfully. Order_ID = {order_id}")

        self.clear_cart()

        self.on_store_changed()

        self.refresh_sales_orders()

    # =========================================================
    # TAB 3: Reports
    # =========================================================
    def build_reports_tab(self):
        top = ttk.LabelFrame(self.tab_reports, text="supply -> warehouse -> transfer")
        top.pack(fill="x", padx=10, pady=10)

        ttk.Label(top, text="Select Report:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.rep_var = tk.StringVar()
        self.rep_cb = ttk.Combobox(
            top,
            textvariable=self.rep_var,
            state="readonly",
            width=45,
            values=[
                "Total sales per day",
                "Total sales per month",
                "Orders by a specific customer",
                "Best-selling products",
                "Orders processed by each employee"
            ]
        )
        self.rep_cb.grid(row=0, column=1, padx=6, pady=4, sticky="w")
        self.rep_cb.current(0)

        self.rep_var.trace("w", self.on_report_selected)

        self.rep_customer_lbl = ttk.Label(top, text="Customer_ID (only for 'Orders by customer'):")
        self.rep_customer_lbl.grid(row=1, column=0, sticky="w", padx=6,pady=4)
        self.rep_customer_id = tk.StringVar()
        self.rep_customer_entry = ttk.Entry(top, textvariable=self.rep_customer_id, width=15)
        self.rep_customer_entry.grid(row=1, column=1, padx=6, pady=4, sticky="w")

        ttk.Button(top, text="Run", command=self.run_report).grid(row=0, column=2, rowspan=2, padx=10)
        ttk.Button(top, text="Show Chart", command=self.show_chart).grid(row=0, column=3, rowspan=2, padx=10)


        table_frame = ttk.Frame(self.tab_reports)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.rep_table = ttk.Treeview(table_frame, show="headings")
        self.rep_table.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.rep_table.yview)
        self.rep_table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        

    def on_report_selected(self, *args):
        if self.rep_var.get() == "Orders by a specific customer":
            self.rep_customer_lbl.grid()
            self.rep_customer_entry.grid()
        else:
            self.rep_customer_lbl.grid_forget()
            self.rep_customer_entry.grid_forget()
            
            
    def run_report(self):
        report_type = self.rep_var.get()

        try:
            if report_type == "Total sales per day":
                cols, rows = db.report_total_sales_per_day()
            elif report_type == "Total sales per month":
                cols, rows = db.report_total_sales_per_month()
            elif report_type == "Orders by a specific customer":
                # Get Customer ID from the input field
                customer_id = safe_int(self.rep_customer_id.get())
                if customer_id is None:
                    messagebox.showerror("Error", "Enter a Customer ID for this report.")
                    return
                cols, rows = db.report_orders_by_customer(customer_id)
            elif report_type == "Best-selling products":
                # Optional: you can change the limit if needed
                cols, rows = db.report_best_selling_products(limit=20)
            elif report_type == "Orders processed by each employee":
                cols, rows = db.report_orders_processed_by_employee()
            else:
                messagebox.showerror("Error", "Please select a valid report.")
                return
            
            self._last_report_type = report_type
            self._last_cols = cols
            self._last_rows = rows
            self.set_report_table(cols, rows)

        except Exception as e:
            messagebox.showerror("Report Error", str(e))

    def set_report_table(self, cols, rows):
        for r in self.rep_table.get_children():
            self.rep_table.delete(r)

        self.rep_table["columns"] = cols
        for col in cols:
            self.rep_table.heading(col, text=col)
            self.rep_table.column(col, width=170)

        for row in rows:
            self.rep_table.insert("", "end", values=row)
    
    def show_chart(self):
        if not self._last_report_type or self._last_rows is None:
            messagebox.showerror("Chart", "Run a report first, then click Show Chart.")
            return

        rtype = self._last_report_type
        rows = list(self._last_rows)

        # Only for 1,2,4 as you requested
        allowed = {
            "Total sales per day",
            "Total sales per month",
            "Best-selling products",
        }
        if rtype not in allowed:
            messagebox.showinfo("Chart", "Chart is available only for reports 1, 2, and 4.")
            return

        # Create a popup window
        win = tk.Toplevel(self.app)
        win.title(f"Chart - {rtype}")
        win.geometry("900x500")

        fig = Figure(figsize=(9, 4.5), dpi=100)
        ax = fig.add_subplot(111)

        if rtype == "Total sales per day":
            # rows: (Order_Date, SUM(Total_Amount))
            # sort ascending by date for nicer plot
            rows_sorted = sorted(rows, key=lambda r: str(r[0]))
            x = [str(r[0]) for r in rows_sorted]
            y = [float(r[1] or 0) for r in rows_sorted]

            ax.plot(x, y, marker="o")
            ax.set_title("Total Sales per Day")
            ax.set_xlabel("Order Date")
            ax.set_ylabel("Total Sales")
            ax.tick_params(axis="x", rotation=45)

        elif rtype == "Total sales per month":
            # rows: (Month 'YYYY-MM', SUM(Total_Amount))
            rows_sorted = sorted(rows, key=lambda r: str(r[0]))
            x = [str(r[0]) for r in rows_sorted]
            y = [float(r[1] or 0) for r in rows_sorted]

            ax.bar(x, y)
            ax.set_title("Total Sales per Month")
            ax.set_xlabel("Month")
            ax.set_ylabel("Total Sales")
            ax.tick_params(axis="x", rotation=45)

        elif rtype == "Best-selling products":
            # rows: (Item_Name, Total_Quantity, Total_Sales)
            # Your db.report_best_selling_products returns:
            # cols = ["Item Name", "Total Quantity Sold", "Total Sales"]
            names = [str(r[0]) for r in rows]
            total_sales = [float(r[2] or 0) for r in rows]

            # Show biggest on top (nice for barh)
            zipped = sorted(zip(names, total_sales), key=lambda t: t[1])
            names_sorted = [t[0] for t in zipped]
            sales_sorted = [t[1] for t in zipped]

            ax.barh(names_sorted, sales_sorted)
            ax.set_title("Best-selling Products (by Total Sales)")
            ax.set_xlabel("Total Sales")
            ax.set_ylabel("Product")

        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        toolbar = NavigationToolbar2Tk(canvas, win)
        toolbar.update()
        toolbar.pack()


