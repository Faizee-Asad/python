# 1. Project Structure

```
DineDashPOS/
├── main.py (entry point only)
├── config/
│   ├── __init__.py
│   ├── settings.py (Style class, constants)
│   └── database_config.py
├── core/
│   ├── __init__.py
│   ├── app.py (App class)
│   └── license_manager.py
├── database/
│   ├── __init__.py
│   ├── connection.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── table.py
│   │   ├── order.py
│   │   └── report.py
├── ui/
│   ├── __init__.py
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── license_screen.py
│   │   ├── login_screen.py
│   │   ├── table_screen.py
│   │   ├── order_screen.py
│   │   ├── settings_screen.py
│   │   ├── reports_screen.py
│   │   └── stats_screen.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── stat_cards.py
│   │   ├── product_card.py
│   │   └── animated_button.py
├── utils/
│   ├── __init__.py
│   ├── image_manager.py
│   ├── printer_manager.py
│   └── export_manager.py
└── requirements.txt
```

# 2. Database Restructuring Strategy
* Split database.py into:

	* connection.py: Database connection and table creation
	* models/user.py: All user-related operations
	* models/product.py: Product and inventory operations
	* models/table.py: Table management operations
	* models/order.py: Order and order_items operations
	* models/report.py: Analytics and reporting queries