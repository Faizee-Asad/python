# 

```
restaurant-pos/
│
├── README.md                  # Project description, setup instructions
├── requirements.txt           # Python dependencies
├── main.py                    # Entry point for the app
│
├── pos_app/                   # Main application package
│   ├── __init__.py
│   ├── gui/                   # GUI related files
│   │   ├── __init__.py
│   │   ├── main_window.py     # POS main window
│   │   ├── admin_panel.py     # Admin panel window
│   │   └── login_window.py    # Admin login
│   │
│   ├── database/              # Database related files
│   │   ├── __init__.py
│   │   ├── db_manager.py      # SQLite connection and queries
│   │   └── schema.sql         # Initial DB schema
│   │
│   ├── logic/                 # Business logic
│   │   ├── __init__.py
│   │   ├── billing.py         # Bill generation logic
│   │   └── products.py        # Product operations
│   │
│   └── utils/                 # Helper utilities
│       ├── __init__.py
│       ├── printer.py         # Bill printing function
│       └── constants.py       # App constants (e.g., colors, fonts)
│
├── data/                      # Data storage
│   ├── pos.db                 # SQLite database file
│   └── receipts/              # Saved bills/receipts
│
└── assets/                    # Images, icons, etc.
    └── logo.png

```

## setup venv      
* python -m venv venv
* venv\Scripts\activate.bat
* deactivate

```
# V1 

## 1 Scheme.sql
## 2 db_manager.py
## 3 constants.py
## 4 login_window.py
## 5 main_window.py
## 6 main.py
## run 

# V2 

## 1 pos_app/database/schema.sql
## 2 pos_app/database/db_manager.py
## 3 pos_app/logic/billing.py
## 4 pos_app/logic/products.py
## 5 pos_app/utils/constants.py
## 6 pos_app/gui/main_window.py
## run

# V3 

## 1 pos_app/gui/admin_panel.py
## 2 pos_app/database/db_manager.py
## 3 pos_app/gui/main_window.py
## run

# v4 
## 1 pos_app/utils/printer.py
## 2 pos_app/logic/billing.py
## 3 data/receipts/
```

```
venv\Scripts\activate
pip install pyinstaller

pyinstaller --noconfirm --onefile --windowed main.py ^
--add-data "data/pos.db;data" ^
--add-data "data/receipts;data/receipts" ^
--add-data "assets;assets"

pyinstaller --onefile --add-data "pos_app/database/schema.sql;pos_app/database" main.py

# temp database
rmdir /s /q build dist
pyinstaller --onefile --add-data "pos_app/database/schema.sql;pos_app/database" main.py

# parmenet database
rmdir /s /q build dist __pycache__
del main.spec

pyinstaller --onefile --add-data "pos_app\database\schema.sql;pos_app\database" main.py

```