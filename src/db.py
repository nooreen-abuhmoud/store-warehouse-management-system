import mysql.connector
import db_config


# Connection
# ----------------------------
def get_connection():
    return mysql.connector.connect(
        host=db_config.DB_HOST,
        user=db_config.DB_USER,
        password=db_config.DB_PASSWORD,
        database=db_config.DB_NAME,
        port=db_config.DB_PORT
    )


# Customers Managment
# ----------------------------
def customer_insert(name: str, phone: str, address: str = "") -> int:
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO Customer (Name, Phone, Address) VALUES (%s, %s, %s)", (name, phone, address))
        con.commit()
        return cur.lastrowid
    finally:
        cur.close()
        con.close()

def customer_update(customer_id: int, name: str, phone: str, address: str = "") -> int:
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute(
            "UPDATE Customer SET Name=%s, Phone=%s, Address=%s WHERE Customer_ID=%s",
            (name, phone, address, customer_id)
        )
        con.commit()
        return cur.rowcount
    finally:
        cur.close()
        con.close()

def customer_delete(customer_id: int) -> int:
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("DELETE FROM Customer WHERE Customer_ID=%s", (customer_id,))
        con.commit()
        return cur.rowcount
    finally:
        cur.close()
        con.close()

def customer_get_by_id(customer_id: int):
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute(
            "SELECT Customer_ID, Name, Phone, Address FROM Customer WHERE Customer_ID=%s",
            (customer_id,)
        )
        return cur.fetchone()
    finally:
        cur.close()
        con.close()

def customer_get_all():
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("SELECT Customer_ID, Name, Phone, Address FROM Customer ORDER BY Customer_ID DESC")
        return cur.fetchall()
    finally:
        cur.close()
        con.close()

def customer_search_by_name(keyword: str):
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute(
            "SELECT Customer_ID, Name, Phone, Address FROM Customer WHERE Name LIKE %s ORDER BY Customer_ID DESC",
            (f"%{keyword}%",)
        )
        return cur.fetchall()
    finally:
        cur.close()
        con.close()

# ----------------------------
# Sales / Orders
# ----------------------------
def store_get_all():
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("SELECT Store_ID, Name FROM Store ORDER BY Store_ID")
        return cur.fetchall()
    finally:
        cur.close()
        con.close()


def employee_get_store_staff(store_id: int):
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("""
            SELECT e.Employee_ID, e.Name, e.Role
            FROM Employee e
            JOIN Store_Employee se ON e.Employee_ID = se.Employee_ID
            WHERE se.Store_ID = %s
            ORDER BY e.Employee_ID
        """, (store_id,))
        return cur.fetchall()
    finally:
        cur.close()
        con.close()

def inventory_items_for_store(store_id: int):
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("""
            SELECT si.Item_ID, i.Item_Name, si.Selling_Price, si.Quantity_Store
            FROM Store_Inventory si
            JOIN Item i ON i.Item_ID = si.Item_ID
            WHERE si.Store_ID = %s
            ORDER BY i.Item_Name
        """, (store_id,))
        return cur.fetchall()
    finally:
        cur.close()
        con.close()

def get_category_for_item(item_id: int):
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("""
            SELECT c.Category_ID, c.Category_Name
            FROM Category c
            JOIN Item i ON c.Category_ID = i.Category_ID
            WHERE i.Item_ID = %s
        """, (item_id,))
        return cur.fetchone()
    finally:
        cur.close()
        con.close()

def _get_or_create_transfer_header(cur, warehouse_id: int, store_id: int, employee_id: int,
                                  transfer_date, transfer_ids_by_wh: dict) -> int:

    if warehouse_id in transfer_ids_by_wh:
        return transfer_ids_by_wh[warehouse_id]

    cur.execute("""
        INSERT INTO Stock_Transfer (Warehouse_ID, Store_ID, Employee_ID, Transfer_Date)
        VALUES (%s, %s, %s, %s)
    """, (warehouse_id, store_id, employee_id, transfer_date))
    transfer_id = cur.lastrowid
    transfer_ids_by_wh[warehouse_id] = transfer_id
    return transfer_id


def _increase_store_inventory(cur, store_id: int, item_id: int, qty: int):
    cur.execute("""
        UPDATE Store_Inventory
        SET Quantity_Store = Quantity_Store + %s
        WHERE Store_ID=%s AND Item_ID=%s
    """, (qty, store_id, item_id))


def _decrease_warehouse_stock(cur, warehouse_id: int, item_id: int, qty: int):
    cur.execute("""
        UPDATE Stock
        SET Quantity_Warehouse = Quantity_Warehouse - %s
        WHERE Warehouse_ID=%s AND Item_ID=%s
    """, (qty, warehouse_id, item_id))


def _upsert_transfer_detail(cur, transfer_id: int, item_id: int, qty: int):
    cur.execute("""
        SELECT Quantity_Transferred
        FROM StockTransfer_Detail
        WHERE Transfer_ID=%s AND Item_ID=%s
    """, (transfer_id, item_id))
    existing = cur.fetchone()

    if existing:
        cur.execute("""
            UPDATE StockTransfer_Detail
            SET Quantity_Transferred = Quantity_Transferred + %s
            WHERE Transfer_ID=%s AND Item_ID=%s
        """, (qty, transfer_id, item_id))
    else:
        cur.execute("""
            INSERT INTO StockTransfer_Detail (Transfer_ID, Item_ID, Quantity_Transferred)
            VALUES (%s, %s, %s)
        """, (transfer_id, item_id, qty))


def _get_total_warehouse_available(cur, item_id: int) -> int:
    cur.execute("""
        SELECT COALESCE(SUM(Quantity_Warehouse), 0)
        FROM Stock
        WHERE Item_ID=%s
    """, (item_id,))
    return int(cur.fetchone()[0])


def _auto_transfer_shortage_multi_warehouse(cur, store_id: int, employee_id: int, transfer_date,
                                            item_id: int, shortage: int, transfer_ids_by_wh: dict):

    if shortage <= 0:
        return

    total_avail = _get_total_warehouse_available(cur, item_id)
    if total_avail < shortage:
        raise ValueError(
            f"No available quantity for Item {item_id}. "
            f"Warehouse total available={total_avail}, needed={shortage}."
        )

    cur.execute("""
        SELECT Quantity_Store
        FROM Store_Inventory
        WHERE Store_ID=%s AND Item_ID=%s
        FOR UPDATE
    """, (store_id, item_id))
    inv = cur.fetchone()
    if not inv:
        raise ValueError(f"Item {item_id} is not configured in Store_Inventory for Store {store_id}.")

    remaining = shortage

    cur.execute("""
        SELECT Warehouse_ID
        FROM Stock
        WHERE Item_ID=%s AND Quantity_Warehouse > 0
        ORDER BY Quantity_Warehouse DESC
    """, (item_id,))
    wh_ids = [int(r[0]) for r in cur.fetchall()]

    for warehouse_id in wh_ids:
        if remaining <= 0:
            break

        cur.execute("""
            SELECT Quantity_Warehouse
            FROM Stock
            WHERE Warehouse_ID=%s AND Item_ID=%s
            FOR UPDATE
        """, (warehouse_id, item_id))
        row = cur.fetchone()
        if not row:
            continue

        wh_qty = int(row[0])
        if wh_qty <= 0:
            continue

        take_qty = wh_qty if wh_qty < remaining else remaining

        transfer_id = _get_or_create_transfer_header(
            cur, warehouse_id, store_id, employee_id, transfer_date, transfer_ids_by_wh
        )

        _upsert_transfer_detail(cur, transfer_id, item_id, take_qty)

        _decrease_warehouse_stock(cur, warehouse_id, item_id, take_qty)
        _increase_store_inventory(cur, store_id, item_id, take_qty)

        remaining -= take_qty

    if remaining > 0:
        raise ValueError(
            f"Warehouse stock changed during transfer. Still need {remaining} for Item {item_id}."
        )

def create_customer_order(store_id: int, employee_id: int, customer_id: int, order_date, cart_lines):
    if not cart_lines:
        raise ValueError("Cart is empty.")

    con = get_connection()
    try:
        con.start_transaction()
        cur = con.cursor()

        transfer_ids_by_wh = {}
        total_amount = 0.0

        for line in cart_lines:
            item_id = int(line["item_id"])
            qty_needed = int(line["qty"])

            if qty_needed <= 0:
                raise ValueError(f"Invalid quantity for item {item_id}. Quantity must be greater than zero.")

            cur.execute("""
                SELECT Selling_Price, Quantity_Store
                FROM Store_Inventory
                WHERE Store_ID=%s AND Item_ID=%s
                FOR UPDATE
            """, (store_id, item_id))
            inv = cur.fetchone()

            if not inv:
                raise ValueError(f"Item {item_id} is not available in Store_Inventory for Store {store_id}.")

            selling_price, store_qty = float(inv[0]), int(inv[1])

            if store_qty < qty_needed:
                shortage = qty_needed - store_qty
                _auto_transfer_shortage_multi_warehouse(
                    cur=cur,
                    store_id=store_id,
                    employee_id=employee_id,
                    transfer_date=order_date,
                    item_id=item_id,
                    shortage=shortage,
                    transfer_ids_by_wh=transfer_ids_by_wh
                )

            line["unit_price"] = selling_price
            total_amount += qty_needed * selling_price

        cur.execute("""
            INSERT INTO Customer_Order (Customer_ID, Employee_ID, Store_ID, Order_Date, Total_Amount)
            VALUES (%s, %s, %s, %s, %s)
        """, (customer_id, employee_id, store_id, order_date, total_amount))

        order_id = cur.lastrowid

        for line in cart_lines:
            item_id = int(line["item_id"])
            qty = int(line["qty"])
            unit_price = float(line["unit_price"])

            cur.execute("""
                INSERT INTO CustomerOrder_Details (CustomerOrder_ID, Store_ID, Item_ID, Quantity, Unit_Price)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, store_id, item_id, qty, unit_price))

            cur.execute("""
                UPDATE Store_Inventory
                SET Quantity_Store = Quantity_Store - %s
                WHERE Store_ID=%s AND Item_ID=%s
            """, (qty, store_id, item_id))

        con.commit()
        return order_id

    except Exception as e:
        con.rollback()
        raise ValueError(f"Error occurred while creating the order: {str(e)}")
    finally:
        con.close()

# ----------------------------
# Cancel Order Logic
# ----------------------------
def cancel_customer_order(order_id: int, store_id: int):
    if not order_id or not store_id:
        raise ValueError("Order ID and Store ID cannot be empty or None.")

    con = get_connection()
    try:
        con.start_transaction()
        cur = con.cursor()

        cur.execute("""
            SELECT Item_ID, Quantity
            FROM CustomerOrder_Details
            WHERE CustomerOrder_ID = %s
        """, (order_id,))
        order_details = cur.fetchall()

        if not order_details:
            raise ValueError(f"No details found for Order ID {order_id}.")

        for item_id, qty in order_details:
            cur.execute("""
                UPDATE Store_Inventory
                SET Quantity_Store = Quantity_Store + %s
                WHERE Store_ID = %s AND Item_ID = %s
            """, (qty, store_id, item_id))

        cur.execute("""
            DELETE FROM CustomerOrder_Details WHERE CustomerOrder_ID = %s
        """, (order_id,))

        cur.execute("""
            DELETE FROM Customer_Order WHERE CustomerOrder_ID = %s
        """, (order_id,))

        con.commit()

    except Exception as e:
        con.rollback()
        raise Exception(f"Error canceling order {order_id}: {str(e)}")
    finally:
        con.close()

def get_all_orders():
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("""
            SELECT co.CustomerOrder_ID, c.Name, co.Order_Date
            FROM Customer_Order co
            JOIN Customer c ON co.Customer_ID = c.Customer_ID
            ORDER BY co.CustomerOrder_ID DESC
        """)
        return cur.fetchall()
    finally:
        cur.close()
        con.close()


# ----------------------------
# Sales / Orders Reports
# ----------------------------

def report_total_sales_per_day():
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("""
            SELECT Order_Date, SUM(Total_Amount)
            FROM Customer_Order
            GROUP BY Order_Date
            ORDER BY Order_Date DESC
        """)
        cols = ["Order Date", "Total Sales"]
        rows = cur.fetchall()
        return cols, rows
    finally:
        cur.close()
        con.close()


def report_total_sales_per_month():
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("""
            SELECT DATE_FORMAT(Order_Date, '%Y-%m') AS Month, SUM(Total_Amount)
            FROM Customer_Order
            GROUP BY Month
            ORDER BY Month DESC
        """)
        cols = ["Month", "Total Sales"]
        rows = cur.fetchall()
        return cols, rows
    finally:
        cur.close()
        con.close()


def report_orders_by_customer(customer_id: int):
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("""
            SELECT co.CustomerOrder_ID, co.Order_Date, co.Total_Amount
            FROM Customer_Order co
            WHERE co.Customer_ID = %s
            ORDER BY co.Order_Date DESC
        """, (customer_id,))
        cols = ["Order ID", "Order Date", "Total Amount"]
        rows = cur.fetchall()
        return cols, rows
    finally:
        cur.close()
        con.close()


def report_best_selling_products(limit=10):
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("""
            SELECT i.Item_Name, SUM(cod.Quantity) AS Total_Quantity, SUM(cod.Quantity * cod.Unit_Price) AS Total_Sales
            FROM CustomerOrder_Details cod
            JOIN Item i ON i.Item_ID = cod.Item_ID
            GROUP BY i.Item_Name
            ORDER BY Total_Sales DESC
            LIMIT %s
        """, (limit,))
        cols = ["Item Name", "Total Quantity Sold", "Total Sales"]
        rows = cur.fetchall()
        return cols, rows
    finally:
        cur.close()
        con.close()


def report_orders_processed_by_employee():
    con = get_connection()
    cur = con.cursor()
    try:
        cur.execute("""
            SELECT e.Name AS Employee_Name, COUNT(co.CustomerOrder_ID) AS Orders_Processed
            FROM Customer_Order co
            JOIN Employee e ON e.Employee_ID = co.Employee_ID
            GROUP BY e.Name
            ORDER BY Orders_Processed DESC
        """)
        cols = ["Employee Name", "Orders Processed"]
        rows = cur.fetchall()
        return cols, rows
    finally:
        cur.close()
        con.close()
