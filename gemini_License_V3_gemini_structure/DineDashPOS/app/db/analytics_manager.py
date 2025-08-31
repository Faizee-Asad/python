from .base_manager import BaseManager

class AnalyticsManager(BaseManager):
    """
    Manages all complex queries for analytics, reporting, and live statistics.
    """

    # --- Live Stats Dashboard Methods ---
    def get_live_stats(self) -> dict:
        """Gathers a dictionary of various live statistics for the dashboard."""
        stats = {}
        
        # Today's revenue
        self.cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0) as today_sales
            FROM orders 
            WHERE status = 'closed' AND DATE(closed_at) = DATE('now')
        """)
        stats['today_revenue'] = self.cursor.fetchone()['today_sales']

        # Active orders
        self.cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status = 'open'")
        stats['active_orders'] = self.cursor.fetchone()['count']

        # Tables status
        self.cursor.execute("SELECT COUNT(*) FROM tables")
        stats['total_tables'] = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(DISTINCT table_id) FROM orders WHERE status = 'open'")
        stats['occupied_tables'] = self.cursor.fetchone()[0]

        # Average order value today
        self.cursor.execute("""
            SELECT AVG(total_amount) as avg_value
            FROM orders
            WHERE status = 'closed' AND DATE(closed_at) = DATE('now')
        """)
        result = self.cursor.fetchone()
        stats['avg_order_value'] = result['avg_value'] if result and result['avg_value'] is not None else 0

        # Top product today
        self.cursor.execute("""
            SELECT p.name
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE o.status = 'closed' AND DATE(o.closed_at) = DATE('now')
            GROUP BY p.id, p.name
            ORDER BY SUM(oi.quantity) DESC
            LIMIT 1
        """)
        result = self.cursor.fetchone()
        stats['top_product'] = result['name'] if result else "N/A"

        # Active staff (simplified count)
        self.cursor.execute("SELECT COUNT(*) as count FROM users")
        stats['active_staff'] = self.cursor.fetchone()['count']

        # Hourly sales for today
        self.cursor.execute("""
            SELECT strftime('%H', closed_at) as hour, SUM(total_amount) as amount
            FROM orders
            WHERE status = 'closed' AND DATE(closed_at) = DATE('now')
            GROUP BY hour ORDER BY hour
        """)
        stats['hourly_sales'] = {f"{int(row['hour']):02d}:00": row['amount'] for row in self.cursor.fetchall()}

        # Category distribution today
        self.cursor.execute("""
            SELECT p.category, SUM(oi.quantity * oi.price_at_time) as amount
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status = 'closed' AND DATE(o.closed_at) = DATE('now')
            GROUP BY p.category
        """)
        stats['category_distribution'] = {row['category']: row['amount'] for row in self.cursor.fetchall()}
        
        return stats

    # --- Historical Reporting Methods ---
    def get_daily_sales_summary(self) -> dict:
        """Gets a comprehensive summary for the daily sales report."""
        self.cursor.execute("""
            SELECT 
                COUNT(DISTINCT o.id) as total_orders,
                COALESCE(SUM(o.total_amount), 0) as total_sales,
                COALESCE(AVG(o.total_amount), 0) as average_order
            FROM orders o
            WHERE o.status = 'closed' AND DATE(o.closed_at) = DATE('now')
        """)
        summary = dict(self.cursor.fetchone())
        
        self.cursor.execute("""
            SELECT p.category, SUM(oi.quantity * oi.price_at_time) as amount
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            WHERE o.status = 'closed' AND DATE(o.closed_at) = DATE('now')
            GROUP BY p.category
        """)
        summary['sales_by_category'] = {row['category']: row['amount'] for row in self.cursor.fetchall()}
        return summary

    def get_sales_by_period(self, period: str) -> dict:
        """Gets aggregated sales data for a specific period (e.g., 'Last 7 Days')."""
        query_map = {
            "Last 7 Days": " AND closed_at >= DATE('now', '-7 days')",
            "Last 30 Days": " AND closed_at >= DATE('now', '-30 days')",
            "This Month": " AND strftime('%Y-%m', closed_at) = strftime('%Y-%m', 'now')",
            "Last Month": " AND strftime('%Y-%m', closed_at) = strftime('%Y-%m', 'now', '-1 month')"
        }
        
        query = f"""
            SELECT DATE(closed_at) as date, SUM(total_amount) as amount
            FROM orders
            WHERE status = 'closed' {query_map.get(period, '')}
            GROUP BY DATE(closed_at)
            ORDER BY date
        """
        self.cursor.execute(query)
        return {row['date']: row['amount'] for row in self.cursor.fetchall()}

    def get_top_products(self, limit: int = 10) -> list:
        """Gets the best-selling products by quantity sold."""
        self.cursor.execute('''
            SELECT 
                p.name,
                SUM(oi.quantity) as quantity_sold,
                SUM(oi.quantity * oi.price_at_time) as revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.status = 'closed'
            GROUP BY p.id, p.name
            ORDER BY quantity_sold DESC
            LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()

    def get_staff_performance(self) -> list:
        """Gets performance metrics for each staff member."""
        self.cursor.execute('''
            SELECT 
                u.username, u.role,
                COUNT(DISTINCT o.id) as total_orders,
                COALESCE(SUM(o.total_amount), 0) as total_sales,
                COALESCE(AVG(o.total_amount), 0) as average_order
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id AND o.status = 'closed'
            GROUP BY u.id, u.username, u.role
            ORDER BY total_sales DESC
        ''')
        return self.cursor.fetchall()

    def get_order_history(self, date_filter: str = "All Time") -> list:
        """Gets a filterable history of all closed orders."""
        query = '''
            SELECT 
                o.id, o.closed_at, o.total_amount as total,
                t.name as table_name, u.username as user_name
            FROM orders o
            JOIN tables t ON o.table_id = t.id
            JOIN users u ON o.user_id = u.id
            WHERE o.status = 'closed'
        '''
        
        filter_map = {
            "Today": " AND DATE(o.closed_at) = DATE('now')",
            "Last 7 Days": " AND o.closed_at >= DATE('now', '-7 days')",
            "Last 30 Days": " AND o.closed_at >= DATE('now', '-30 days')"
        }
        query += filter_map.get(date_filter, "")
        query += " ORDER BY o.closed_at DESC"
        
        self.cursor.execute(query)
        return self.cursor.fetchall()

    # --- Data Export Methods ---
    def get_all_sales_data_for_export(self) -> list:
        """Gets a comprehensive flat list of all sales data for export."""
        self.cursor.execute('''
            SELECT
                o.closed_at as timestamp, t.name as table_name, u.username as server,
                p.name as product_name, p.category, oi.quantity,
                oi.price_at_time as price
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            JOIN products p ON oi.product_id = p.id
            JOIN users u ON o.user_id = u.id
            JOIN tables t ON o.table_id = t.id
            WHERE o.status = 'closed'
            ORDER BY o.closed_at DESC
        ''')
        return [dict(row) for row in self.cursor.fetchall()]
