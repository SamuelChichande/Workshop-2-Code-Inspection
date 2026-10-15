"""Order processing logic."""
import database
import auth

TAX = 0.15
SEPARATOR = "=============================="


def _process_item(item):
    book = database.get_book(item["book_id"])
    if not book:
        print("Book not found")
        return 0

    qty = item["qty"]
    if qty <= 0:
        print("Invalid quantity")
        return 0

    stock = book[3]
    if stock < qty:
        if stock > 0:
            print("Only " + str(stock) + " units available for " + book[1])
        else:
            print("Book out of stock: " + book[1])
        return 0

    database.update_stock(book[0], stock - qty)
    return book[2] * qty


def _apply_coupon(total, coupon):
    if coupon == "WELCOME10":
        return total * 0.9
    elif coupon == "BLACKFRIDAY":
        return total * 0.5
    elif coupon == "STAFF":
        return total * 0.7
    return total


def _calculate_shipping(shipping):
    if shipping == "express":
        return 10
    elif shipping == "standard":
        return 3
    return 0


def process_order(token, items, coupon=None, shipping="standard", log=None):
    if log is None:
        log = []
    username = auth.sessions.get(token)
    if username is None:
        print("Invalid session")
        return None

    if items == []:
        print("Empty order")
        return None

    total = 0
    for item in items:
        total += _process_item(item)

    total = _apply_coupon(total, coupon)
    total += _calculate_shipping(shipping)
    total += total * TAX

    order_id = len(log) + 1
    database.save_order(order_id, username, total, "PENDING")
    log.append(order_id)
    return round(total, 2)


def print_invoice(username, items):
    print(SEPARATOR)
    print("BOOKSTORE INVOICE")
    print("Customer: " + username)
    print(SEPARATOR)
    subtotal = 0
    for item in items:
        book = database.get_book(item["book_id"])
        line_total = book[2] * item["qty"]
        subtotal = subtotal + line_total
        print(book[1] + " x" + str(item["qty"]) + " = " + str(line_total))
    tax = subtotal * TAX
    print("Subtotal: " + str(round(subtotal, 2)))
    print("Tax: " + str(round(tax, 2)))
    print("Total: " + str(round(subtotal + tax, 2)))
    print(SEPARATOR)


def print_quote(username, items):
    print(SEPARATOR)
    print("BOOKSTORE QUOTE")
    print("Customer: " + username)
    print(SEPARATOR)
    subtotal = 0
    for item in items:
        book = database.get_book(item["book_id"])
        line_total = book[2] * item["qty"]
        subtotal = subtotal + line_total
        print(book[1] + " x" + str(item["qty"]) + " = " + str(line_total))
    tax = subtotal * TAX
    print("Subtotal: " + str(round(subtotal, 2)))
    print("Tax: " + str(round(tax, 2)))
    print("Total: " + str(round(subtotal + tax, 2)))
    print("This quote is valid for 7 days.")
    print(SEPARATOR)


def cancel_order(order_id):
    try:
        conn = database.get_connection()
        conn.execute(f"UPDATE orders SET status = 'CANCELLED' WHERE id = {order_id}")
        conn.commit()
    except Exception:
        pass
