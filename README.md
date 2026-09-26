# StockSense – Inventory Management System

StockSense is a web-based Inventory Management System built with Django. It provides a centralized platform for managing products, warehouses, stock levels, receipts, deliveries, internal transfers, inventory adjustments, and stock movement history.

The system is designed to replace manual inventory registers, spreadsheets, and scattered stock records with a centralized and organized inventory management solution.

---

## 🚀 Features

### 🔐 User Authentication
- User signup and login
- Secure logout
- OTP-based password reset
- Password validation
- Protected dashboard and inventory pages

### 📦 Product Management
- Create and manage products
- Unique SKU/product codes
- Product categories
- Unit of measurement
- Product-level stock tracking

### 🏷️ Category Management
- Create categories
- Update categories
- Delete categories
- Organize products by category

### 🏢 Warehouse Management
- Create warehouses
- Store warehouse addresses
- Create multiple locations inside a warehouse
- Manage locations such as:
  - Receiving
  - Storage
  - Dispatch

### 📊 Stock Management
- Track stock by product and location
- Add stock quantities
- View current stock
- Multi-location stock tracking
- Prevent negative stock during deliveries and transfers

### 🚚 Inventory Operations

#### Receipts
- Create receipts
- Add products and quantities
- Validate receipts
- Automatically increase stock
- Create stock ledger entries

#### Delivery Orders
- Create delivery orders
- Add products and quantities
- Validate deliveries
- Automatically decrease stock
- Prevent delivery when sufficient stock is unavailable

#### Internal Transfers
- Transfer products between locations
- Automatically decrease stock from source
- Automatically increase stock at destination
- Maintain transfer history

#### Inventory Adjustments
- Record physically counted stock
- Compare counted quantity with system quantity
- Automatically update stock
- Record adjustment differences in the ledger

### 📋 Stock Ledger / Move History
Every stock-changing operation is recorded in the centralized stock ledger.

Tracked operations include:

- Receipt
- Delivery
- Transfer In
- Transfer Out
- Adjustment

### 🔔 Reorder Rules
- Configure minimum stock levels
- Configure maximum stock levels
- Configure reorder quantities
- Enable/disable individual reorder rules
- Product and location-specific reorder rules

### 📈 Dashboard
The dashboard provides an overview of inventory activity, including:

- Total stock
- Low-stock items
- Out-of-stock items
- Pending receipts
- Pending deliveries
- Pending internal transfers
- Recent stock movements
- Warehouse-wise stock

---

## 🏗️ Project Architecture

```text
StockSense/
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── inventory/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── operations/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── services/
│       └── stock_service.py
│
├── warehouse/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── dashboard/
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── templates/
│   ├── accounts/
│   ├── inventory/
│   ├── operations/
│   ├── warehouse/
│   └── dashboard/
│
├── static/
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
