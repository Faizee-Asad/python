import sqlite3
import os
from .setup_manager import SetupManager
from .crud_manager import CrudManager
from .order_manager import OrderManager
from .analytics_manager import AnalyticsManager

class DatabaseManager:
    """
    The main orchestrator for all database operations.
    This class initializes the database connection and provides access to all
    specialized manager modules (CRUD, Orders, Analytics).
    """
    def __init__(self, db_name="restaurant_pos.db"):
        """
        Initializes the database connection and all manager modules.
        
        Args:
            db_name: The name of the SQLite database file.
        """
        # Ensure the application data directory exists
        home_dir = os.path.expanduser("~")
        app_data_dir = os.path.join(home_dir, "DineDashPOS")
        os.makedirs(app_data_dir, exist_ok=True)
        db_path = os.path.join(app_data_dir, db_name)
        
        # Establish connection
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row # Allows accessing columns by name
        
        # Initialize all specialized managers
        self.setup = SetupManager(self.conn)
        self.crud = CrudManager(self.conn)
        self.orders = OrderManager(self.conn)
        self.analytics = AnalyticsManager(self.conn)
        
        # Run initial setup (creates tables and seeds data if needed)
        self.setup.initialize_database()

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """Ensures the database connection is closed when the object is destroyed."""
        self.close()
