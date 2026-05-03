from database import SessionLocal
from models import Product

SAMPLE_PRODUCTS = [
    ("Wireless Headphones",    "Over-ear noise-cancelling Bluetooth headphones with 30h battery.", "Electronics",  2499.00, 25),
    ("Mechanical Keyboard",    "Tactile RGB mechanical keyboard, TKL layout, Cherry MX Blue.",     "Electronics",  3799.00, 15),
    ("Running Shoes",          "Lightweight mesh running shoes with cushioned sole.",               "Footwear",      899.00, 40),
    ("Canvas Backpack",        "Water-resistant 30L canvas backpack with laptop compartment.",      "Bags",          1299.00, 30),
    ("Stainless Tumbler",      "600ml double-wall vacuum insulated tumbler, keeps hot/cold 12h.",   "Kitchen",       599.00,  50),
    ("Graphic Novel Vol. 1",   "Award-winning sci-fi graphic novel, full colour, 200 pages.",       "Books",         449.00,  60),
    ("Yoga Mat",               "Non-slip 6mm thick TPE yoga mat with carrying strap.",              "Sports",        799.00,  35),
    ("Desk Lamp",              "LED desk lamp with 3 colour modes and USB-C charging port.",        "Home",          999.00,  20),
    ("Ceramic Coffee Mug",     "Hand-glazed 350ml ceramic mug, microwave and dishwasher safe.",    "Kitchen",       299.00,  80),
    ("Leather Wallet",         "Slim RFID-blocking genuine leather bifold wallet.",                 "Accessories",   749.00,  45),
    ("Portable Speaker",       "IPX7 waterproof Bluetooth 5.0 speaker, 12h playtime.",             "Electronics",  1899.00,  18),
    ("Sunglasses",             "Polarised UV400 sunglasses with acetate frame.",                    "Accessories",   649.00,  55),
]

db = SessionLocal()
try:
    for name, desc, cat, price, stock in SAMPLE_PRODUCTS:
        db.add(Product(
            product_name=name,
            product_description=desc,
            product_category=cat,
            product_price=price,
            product_stock=stock,
        ))
    db.commit()
    print(f"Seeded {len(SAMPLE_PRODUCTS)} products.")
finally:
    db.close()
