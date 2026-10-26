DROP DATABASE IF EXISTS women_handbag_db;
CREATE DATABASE women_handbag_db;
USE women_handbag_db;

-- ------------------------------
--  Master Tables

CREATE TABLE Category (
  Category_ID   INT AUTO_INCREMENT PRIMARY KEY,
  Category_Name VARCHAR(100)
);

CREATE TABLE Item (
  Item_ID      INT AUTO_INCREMENT PRIMARY KEY,
  Item_Name    VARCHAR(150) NOT NULL,
  Category_ID  INT NOT NULL,
    FOREIGN KEY (Category_ID) REFERENCES Category(Category_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE Store (
  Store_ID  INT AUTO_INCREMENT PRIMARY KEY,
  Name      VARCHAR(120) NOT NULL,
  Location  VARCHAR(200) NOT NULL
);

CREATE TABLE Warehouse (
  Warehouse_ID INT PRIMARY KEY,
  Location     VARCHAR(200) NOT NULL,
  Capacity     INT NOT NULL CHECK (Capacity >= 0)
);

CREATE TABLE Supplier (
  Supplier_ID INT AUTO_INCREMENT PRIMARY KEY,
  Name        VARCHAR(120) NOT NULL,
  Phone       VARCHAR(30),
  Email       VARCHAR(120)
);

CREATE TABLE Customer (
  Customer_ID INT AUTO_INCREMENT PRIMARY KEY,
  Name        VARCHAR(120) NOT NULL,
  Phone       VARCHAR(30),
  Address     VARCHAR(200)
);
CREATE TABLE Employee (
  Employee_ID INT AUTO_INCREMENT PRIMARY KEY,
  Name        VARCHAR(120) NOT NULL,
  Role        VARCHAR(60)
);

-- -------------------------
--  ISA Specialization Total + Disjoint 
-- Store_Employee and Warehouse_Employee are subtypes of Employee

CREATE TABLE Store_Employee (
  Employee_ID INT PRIMARY KEY,
  Store_ID    INT NOT NULL,
    FOREIGN KEY (Employee_ID) REFERENCES Employee(Employee_ID)
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (Store_ID) REFERENCES Store(Store_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE Warehouse_Employee (
  Employee_ID  INT PRIMARY KEY,
  Warehouse_ID INT NOT NULL,
    FOREIGN KEY (Employee_ID) REFERENCES Employee(Employee_ID)
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (Warehouse_ID) REFERENCES Warehouse(Warehouse_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);
-- -------------------------
-- Inventory Tables (Composite PKs)

CREATE TABLE Stock (
  Warehouse_ID      INT NOT NULL,
  Item_ID           INT NOT NULL,
  Quantity_Warehouse INT NOT NULL CHECK (Quantity_Warehouse >= 0),
  PRIMARY KEY (Warehouse_ID, Item_ID),
    FOREIGN KEY (Warehouse_ID) REFERENCES Warehouse(Warehouse_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (Item_ID) REFERENCES Item(Item_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE Store_Inventory (
  Store_ID       INT NOT NULL,
  Item_ID        INT NOT NULL,
  Selling_Price  DECIMAL(10,2) NOT NULL CHECK (Selling_Price >= 0),
  Quantity_Store INT NOT NULL CHECK (Quantity_Store >= 0),
  PRIMARY KEY (Store_ID, Item_ID),
    FOREIGN KEY (Store_ID) REFERENCES Store(Store_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (Item_ID) REFERENCES Item(Item_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);
-- -------------------------
-- Customer Orders Header + Weak Details
-- Details references Store_Inventory via (Store_ID, Item_ID)

CREATE TABLE Customer_Order (
  CustomerOrder_ID INT AUTO_INCREMENT PRIMARY KEY,
  Customer_ID      INT NOT NULL,
  Employee_ID      INT NOT NULL,
  Store_ID         INT NOT NULL,
  Order_Date       DATE NOT NULL,
  Total_Amount     DECIMAL(12,2) DEFAULT 0,
    FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (Employee_ID) REFERENCES Employee(Employee_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (Store_ID) REFERENCES Store(Store_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE CustomerOrder_Details (
  CustomerOrder_ID INT NOT NULL,
  Store_ID         INT NOT NULL,
  Item_ID          INT NOT NULL,
  Quantity         INT NOT NULL CHECK (Quantity > 0),
  Unit_Price       DECIMAL(10,2) NOT NULL CHECK (Unit_Price >= 0),
  PRIMARY KEY (CustomerOrder_ID, Item_ID),
    FOREIGN KEY (CustomerOrder_ID) REFERENCES Customer_Order(CustomerOrder_ID)
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (Store_ID, Item_ID) REFERENCES Store_Inventory(Store_ID, Item_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

-- -------------------------
-- Supply Orders Header + Weak Details
-- Supply order is for Warehouse

CREATE TABLE Supply_Order (
  SupplyOrder_ID INT AUTO_INCREMENT PRIMARY KEY,
  Supplier_ID    INT NOT NULL,
  Employee_ID    INT NOT NULL,
  Warehouse_ID   INT NOT NULL,
  Order_Date     DATE NOT NULL,
  Total_Amount   DECIMAL(12,2) DEFAULT 0,
    FOREIGN KEY (Supplier_ID) REFERENCES Supplier(Supplier_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (Employee_ID) REFERENCES Employee(Employee_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (Warehouse_ID) REFERENCES Warehouse(Warehouse_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE Supply_Order_Details (
  SupplyOrder_ID     INT NOT NULL,
  Item_ID            INT NOT NULL,
  Quantity_Purchased INT NOT NULL CHECK (Quantity_Purchased > 0),
  Unit_Cost          DECIMAL(10,2) NOT NULL CHECK (Unit_Cost >= 0),
  PRIMARY KEY (SupplyOrder_ID, Item_ID),
    FOREIGN KEY (SupplyOrder_ID) REFERENCES Supply_Order(SupplyOrder_ID)
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (Item_ID) REFERENCES Item(Item_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

-- -------------------------
-- Stock Transfer Header + Weak Details
-- Transfer from Warehouse -> Store, performed by Employee

CREATE TABLE Stock_Transfer (
  Transfer_ID   INT AUTO_INCREMENT PRIMARY KEY,
  Warehouse_ID  INT NOT NULL,
  Store_ID      INT NOT NULL,
  Employee_ID   INT NOT NULL,
  Transfer_Date DATE NOT NULL,
    FOREIGN KEY (Warehouse_ID) REFERENCES Warehouse(Warehouse_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (Store_ID) REFERENCES Store(Store_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (Employee_ID) REFERENCES Employee(Employee_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE StockTransfer_Detail (
  Transfer_ID        INT NOT NULL,
  Item_ID            INT NOT NULL,
  Quantity_Transferred INT NOT NULL CHECK (Quantity_Transferred > 0),
  PRIMARY KEY (Transfer_ID, Item_ID),
    FOREIGN KEY (Transfer_ID) REFERENCES Stock_Transfer(Transfer_ID)
    ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (Item_ID) REFERENCES Item(Item_ID)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ---------------------------------------------------------------------------

INSERT INTO Category (Category_Name) VALUES
('Handbags'),
('Wallets'),
('Accessories');

INSERT INTO Item (Item_Name, Category_ID) VALUES
('Classic Leather Handbag', 1),
('Mini Crossbody Bag', 1),
('Canvas Tote Bag', 1),
('Slim Leather Wallet', 2),
('Zip Wallet', 2),
('Keychain Charm', 3);

INSERT INTO Store (Name, Location) VALUES
('Downtown Store', 'Ramallah - Downtown');

INSERT INTO Warehouse (Warehouse_ID , Location, Capacity) VALUES
(1,'Industrial Zone Warehouse', 5000);

INSERT INTO Supplier (Name, Phone, Email) VALUES
('LeatherWorks Co.', '+970-599-111111', 'sales@leatherworks.example'),
('UrbanBags Ltd.',   '+970-599-222222', 'orders@urbanbags.example');


INSERT INTO Customer (Name, Phone, Address) VALUES
('Lina Ahmad',  '+970-599-333333', 'Ramallah - Al-Tireh'),
('Hala Saeed',  '+970-599-444444', 'Nablus - City Center'),
('Rana Khalil', '+970-599-555555', 'Birzeit - Near University');

INSERT INTO Employee (Name, Role) VALUES
('Sami Nasser',  'Cashier'),
('Mona Yassin',  'Store Manager'),
('Omar Haddad',  'Warehouse Clerk'),
('Sara Taha',    'Warehouse Manager');

INSERT INTO Store_Employee (Employee_ID, Store_ID) VALUES
(1, 1),
(2, 1);


INSERT INTO Warehouse_Employee (Employee_ID, Warehouse_ID) VALUES
(3, 1),
(4, 1);

INSERT INTO Stock (Warehouse_ID, Item_ID, Quantity_Warehouse) VALUES
(1, 1, 120),
(1, 2, 200),
(1, 3, 150),
(1, 4, 300),
(1, 5, 250),
(1, 6, 500);

INSERT INTO Store_Inventory (Store_ID, Item_ID, Selling_Price, Quantity_Store) VALUES
(1, 1, 249.99, 15),
(1, 2, 149.99, 20),
(1, 3,  89.99, 25),
(1, 4,  59.99, 30),
(1, 5,  74.99, 28),
(1, 6,  14.99, 60);

INSERT INTO Customer_Order (Customer_ID, Employee_ID, Store_ID, Order_Date, Total_Amount) VALUES
(1, 1, 1, '2026-01-10', 329.97),
(2, 2, 1, '2026-01-11', 149.94);

INSERT INTO CustomerOrder_Details (CustomerOrder_ID, Store_ID, Item_ID, Quantity, Unit_Price) VALUES
(1, 1, 2, 1, 149.99),
(1, 1, 3, 2,  89.99),
(2, 1, 6, 5,  14.99),
(2, 1, 5, 1,  74.99);

INSERT INTO Supply_Order (Supplier_ID, Employee_ID, Warehouse_ID, Order_Date, Total_Amount) VALUES
(1, 4, 1, '2026-01-05', 2250.00),
(2, 3, 1, '2026-01-08', 1420.00);

INSERT INTO Supply_Order_Details (SupplyOrder_ID, Item_ID, Quantity_Purchased, Unit_Cost) VALUES
(1, 1, 20, 80.00),
(1, 4, 50, 13.00),
(2, 2, 30, 45.00),
(2, 6, 80,  0.88);

INSERT INTO Stock_Transfer (Warehouse_ID, Store_ID, Employee_ID, Transfer_Date) VALUES
(1, 1, 3, '2026-01-12');

INSERT INTO StockTransfer_Detail (Transfer_ID, Item_ID, Quantity_Transferred) VALUES
(1, 5, 10),
(1, 6, 30);



 
