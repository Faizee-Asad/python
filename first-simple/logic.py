def calculate_total(cart):
    """Calculate total price from cart items."""
    total = sum(item[2] for item in cart)  # item[2] is price
    return total

