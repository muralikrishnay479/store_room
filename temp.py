import csv
import random
from datetime import datetime, timedelta

# Generate mock data
def generate_mock_data():
    # Categories
    categories = ['Electronics', 'Fashion', 'Home Appliances', 'Books', 'Toys']
    vendors = ['vendor1', 'vendor2', 'vendor3']
    products = []
    orders = []
    reviews = []

    # Create mock products
    for i in range(1, 21):  # 20 products
        product = {
            "name": f"Product {i}",
            "description": f"This is the description for Product {i}",
            "category": random.choice(categories),
            "price": round(random.uniform(10, 500), 2),
            "regular_price": round(random.uniform(500, 1000), 2),
            "stock": random.randint(10, 100),
            "shipping": round(random.uniform(5, 50), 2),
            "status": random.choice(["Published", "Draft", "Disabled"]),
            "featured": random.choice([True, False]),
            "vendor": random.choice(vendors),
            "slug": f"product-{i}",
            "sku": f"SKU{i:03d}",
            "date": datetime.now() - timedelta(days=random.randint(1, 365))
        }
        products.append(product)

    # Create mock orders
    for i in range(1, 31):  # 30 orders
        order = {
            "order_id": f"ORD{i:03d}",
            "customer": f"customer{i}@example.com",
            "sub_total": round(random.uniform(50, 500), 2),
            "shipping": round(random.uniform(5, 50), 2),
            "tax": round(random.uniform(2, 20), 2),
            "service_fee": round(random.uniform(1, 10), 2),
            "total": round(random.uniform(100, 1000), 2),
            "payment_status": random.choice(["Paid", "Processing", "Failed"]),
            "payment_method": random.choice(["PayPal", "Stripe", "RazorPay"]),
            "order_status": random.choice(["Pending", "Processing", "Shipped", "Fulfilled", "Cancelled"]),
            "date": datetime.now() - timedelta(days=random.randint(1, 365))
        }
        orders.append(order)

    # Create mock reviews
    for i in range(1, 51):  # 50 reviews
        review = {
            "user": f"user{i}@example.com",
            "product": random.choice(products)["name"],
            "review": f"This is a review for Product {i}",
            "reply": f"Reply to review {i}",
            "rating": random.randint(1, 5),
            "date": datetime.now() - timedelta(days=random.randint(1, 365))
        }
        reviews.append(review)

    # Save data to CSV
    save_to_csv("products.csv", products)
    save_to_csv("orders.csv", orders)
    save_to_csv("reviews.csv", reviews)

def save_to_csv(filename, data):
    keys = data[0].keys()  # Column names from dictionary keys
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

# Generate mock data
generate_mock_data()
