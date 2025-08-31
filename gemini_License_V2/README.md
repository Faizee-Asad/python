## Generate a Key: Run the generate_key.py script from your terminal (python generate_key.py). It will print a valid license key. Copy this key.

### KEY = "VkFMSUQtTElDRU5TRS1GT1ItRElORURBU0g="

## Re-bundle Your .exe: When you are ready to distribute, remember to run the PyInstaller command again on the updated main.py to create a new .exe that includes the licensing system.

### python -m PyInstaller --windowed --onefile --exclude-module escpos.printer.cups --exclude-module escpos.printer.lp main.py


__________________________________________________________________________________________________________________________________

This completes the POS system code. The application now includes:

License Screen: Software activation with license key validation
Login Screen: User selection with role-based access
Table Screen: Floor management with table status visualization
Order Screen: Menu browsing, order management, and payment processing
Settings Screen: Management of users, tables, and products with image support
Reports Screen: Comprehensive reporting with charts and Excel export
Stats Screen: Live dashboard with auto-updating statistics and charts
Key features implemented:

Role-based access control (Admin vs Staff)
Product image management
Thermal printer support with fallback to file
Real-time statistics with auto-refresh
Data visualization with matplotlib
Excel export functionality
Responsive UI with modern design
Error handling and user feedback
The system is now fully functional and ready to use. Make sure you have the database.py file that handles all the database operations, and install the required dependencies:

Bash

pip install customtkinter pillow python-escpos openpyxl pandas matplotlib

```
System Overview
This is a DineDash POS - a restaurant point-of-sale system built with Python using CustomTkinter for the UI and SQLite for the database.

Key Components:
main.py - Frontend/UI Layer
Modern dark theme UI with custom styling
7 main screens:
LicenseScreen: Software activation/licensing
LoginScreen: User authentication
TableScreen: Restaurant floor/table management
OrderScreen: Order taking and menu management
SettingsScreen: Admin panel for users, tables, and products
ReportsScreen: Sales analytics and reporting
StatsScreen: Live dashboard with real-time metrics
database.py - Backend/Data Layer
SQLite database with comprehensive schema
8 main tables:
settings: App configuration and license status
users: Staff accounts with roles (Admin/Server)
products: Menu items with categories and images
tables: Restaurant tables with capacity
orders: Order tracking with status
order_items: Individual items in orders
feedback: Customer ratings/reviews
inventory: Stock management
Key Features:
Role-based access: Admins have full access, Servers have limited access
Image support: Products can have images stored locally
Thermal printer support: With fallback to file-based receipts
Real-time updates: Live dashboard refreshes every 5 seconds
Comprehensive reporting: Daily/monthly sales, top products, staff performance
Excel export: Reports can be exported to Excel files
Inventory tracking: Low stock alerts
Multi-table management: Track occupied/available tables
Technical Stack:
UI: CustomTkinter, Tkinter, PIL
Database: SQLite3
Charts: Matplotlib
Export: Pandas, Openpyxl
Printing: python-escpos (optional)
Workflow:
License activation → Login → Select table
Take order → Add items → Settle payment
Print receipt → Table becomes available
Admin can view reports, manage products/users/tables
The system is well-structured with clear separation between UI and data layers, comprehensive error handling, and a modern, professional interface.
```