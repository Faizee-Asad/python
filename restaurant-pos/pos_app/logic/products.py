from pos_app.database.db_manager import DBManager

class ProductService:
    def __init__(self):
        self.db = DBManager()

    def list_products(self, search: str | None = None):
        return self.db.get_products(search)

    def add(self, name: str, price: float):
        self.db.add_product(name, price)

    def update(self, product_id: int, name: str, price: float):
        self.db.update_product(product_id, name, price)

    def delete(self, product_id: int):
        self.db.delete_product(product_id)
