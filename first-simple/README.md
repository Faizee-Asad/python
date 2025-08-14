```
my_gui_app/
│
├── main.py             # Entry point: runs the app
├── gui.py              # All GUI code here (Tkinter, PyQt, etc.)
├── logic.py            # Business logic / calculations
├── database.py         # DB handling (if using SQLite)
├── utils.py            # Helper functions
│
├── data/               # App data
│   └── app.db          # SQLite database (optional)
│
├── assets/             # Icons, images, etc.
│   └── logo.png
│
├── requirements.txt    # Dependencies
└── README.md           # About the project

```

# 💡 For your restaurant POS practice project: v1

* main.py → Starts app
* gui.py → Main window + admin window
* logic.py → Bill calculation, total, quantity handling
* database.py → Load/add products from SQLite
* utils.py → Helper for printing bills, formatting



# v2

# Restaurant POS (Tkinter + SQLite)

## Features
- Product list with prices
- Add to cart & calculate total
- Admin login (default: admin / 1234)
- Add, Edit, Delete products in Admin Panel


