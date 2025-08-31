import sqlite3

class BaseManager:
    """
    A base class for all database manager modules.
    Its primary purpose is to hold a reference to the database connection object,
    making it available to all manager classes that inherit from it.
    """
    def __init__(self, connection: sqlite3.Connection):
        """
        Initializes the manager with the active database connection.

        Args:
            connection: The sqlite3 connection object.
        """
        self.conn = connection
        self.cursor = connection.cursor()
