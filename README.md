# Store & Warehouse Management System

A desktop database application for managing a retail store and its warehouse. The project was originally developed as a university **Database Systems** team project and is presented here as a cleaned portfolio version.

## Overview

The system centralizes common store and warehouse operations in one desktop application. It supports product and supplier management, inventory tracking, supply orders, warehouse-to-store transfers, customer sales, and reporting.

## Tech Stack

- **Python**
- **Tkinter / ttk** for the desktop UI
- **MySQL** for the relational database
- **mysql-connector-python** for database access
- **Matplotlib** for charts and reports

## Main Features

- Customer management (create, update, delete, search)
- Employee, category, item, supplier, store, and warehouse management
- Warehouse stock and store inventory tracking
- Supply-order management
- Warehouse-to-store stock transfers
- Customer sales and order processing
- Automatic warehouse-to-store stock transfer when a sale needs additional stock
- Order cancellation with inventory restoration
- Transaction-based order processing with commit/rollback handling
- Sales and inventory reports with charts

## Project Structure

```text
store-warehouse-management-system/
├── src/
│   ├── app.py          # Main Tkinter application
│   ├── db.py           # Database operations and sales/order logic
│   ├── db_config.py    # Environment-based DB configuration
│   └── sales.py        # Customer, sales, and sales-report UI logic
├── database/
│   └── schema_and_seed.sql
├── docs/
│   └── ER-diagram.pdf
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Database Design

The relational schema models customers, employees, stores, warehouses, suppliers, items, inventory, customer orders, supply orders, and stock transfers.

The ER diagram is available in [`docs/ER-diagram.pdf`](docs/ER-diagram.pdf).

## Setup

### 1. Prerequisites

Install:

- Python 3.10+
- MySQL Server 8+

### 2. Clone the repository

```bash
git clone <your-repository-url>
cd store-warehouse-management-system
```

### 3. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create the MySQL database

Run:

```bash
mysql -u root -p < database/schema_and_seed.sql
```

Or open `database/schema_and_seed.sql` in MySQL Workbench and execute it.

### 6. Configure database credentials

Copy `.env.example` to `.env`:

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

Then edit `.env` with your local MySQL credentials:

```env
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=women_handbag_db
DB_PORT=3306
```

> **Security:** `.env` is ignored by Git and should never be committed.

### 7. Run the application

```bash
python src/app.py
```

## Notes for Reviewers

This is a collaborative academic project. This public portfolio version intentionally excludes course reports, student IDs, local cache files, and database credentials. The included SQL file uses demonstration data to make the application easier to evaluate locally.

## Security Improvements in This Portfolio Version

The original local project stored database credentials directly in a Python configuration file. This portfolio version reads credentials from environment variables instead and includes only a safe `.env.example` template.
