from dataclasses import dataclass
from typing import List, Dict
from pos_app.utils.constants import TAX_RATE

@dataclass
class CartItem:
    product_id: int
    name: str
    price: float
    qty: int

    @property
    def line_total(self) -> float:
        return round(self.price * self.qty, 2)

def calculate_totals(cart: List[CartItem]) -> Dict[str, float]:
    subtotal = round(sum(i.line_total for i in cart), 2)
    tax = round(subtotal * TAX_RATE, 2)
    total = round(subtotal + tax, 2)
    return {"subtotal": subtotal, "tax": tax, "total": total}
