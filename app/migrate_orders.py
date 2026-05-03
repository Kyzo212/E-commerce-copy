"""
Run once to create the orders and order_items tables.
"""
from database import Base, engine
from models import Order, OrderItem

Base.metadata.create_all(engine)
print("orders and order_items tables created.")
