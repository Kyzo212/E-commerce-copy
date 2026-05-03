from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id        = Column(Integer, primary_key=True, autoincrement=True)
    supplier_name      = Column(String(120), nullable=False)
    supplier_email     = Column(String(120), nullable=True)
    supplier_phone     = Column(String(30), nullable=True)
    supplier_address   = Column(Text, nullable=True)
    supplier_is_active = Column(Boolean, nullable=False, default=True)
    created_at         = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "supplier_id":        self.supplier_id,
            "supplier_name":      self.supplier_name,
            "supplier_email":     self.supplier_email or "",
            "supplier_phone":     self.supplier_phone or "",
            "supplier_address":   self.supplier_address or "",
            "supplier_is_active": bool(self.supplier_is_active),
            "created_at":         self.created_at.isoformat() if self.created_at else "",
        }

    def __repr__(self):
        return f"<Supplier id={self.supplier_id} name={self.supplier_name!r}>"


class AdminProfile(Base):
    __tablename__ = "admin_profiles"

    admin_profile_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id          = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    created_at       = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="admin_profile")

    def __repr__(self):
        return f"<AdminProfile user_id={self.user_id}>"


class SellerProfile(Base):
    __tablename__ = "seller_profiles"

    seller_profile_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id           = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    approved_at       = Column(DateTime, nullable=True)
    created_at        = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="seller_profile")

    def __repr__(self):
        return f"<SellerProfile user_id={self.user_id}>"

class Product(Base):
    __tablename__ = "products"

    product_id          = Column(Integer, primary_key=True, autoincrement=True)
    product_name        = Column(String(120), nullable=False)
    product_description = Column(Text, nullable=True)
    product_category    = Column(String(80), nullable=True)
    product_price       = Column(Numeric(10, 2), nullable=False)
    product_stock       = Column(Integer, default=0, nullable=True)
    product_image       = Column(String(500), nullable=True)

    def to_dict(self):
        return {
            "product_id":          self.product_id,
            "product_name":        self.product_name,
            "product_description": self.product_description or "",
            "product_category":    self.product_category or "",
            "product_price":       str(self.product_price),
            "product_stock":       self.product_stock or 0,
            "product_image":       self.product_image or "",
        }

    def __repr__(self):
        return f"<Product id={self.product_id} name={self.product_name!r}>"


class User(Base):
    __tablename__ = "users"

    user_id           = Column(Integer, primary_key=True, autoincrement=True)
    username          = Column(String(80),  unique=True, nullable=False)
    email             = Column(String(120), unique=True, nullable=False)
    password          = Column(String(256), nullable=False)
    role              = Column(String(20), nullable=False, default="customer")  # 'customer' | 'admin'
    seller_status     = Column(String(20), nullable=False, default="none")  # 'none' | 'pending' | 'approved'
    is_active         = Column(Boolean, nullable=False, default=True)
    created_at        = Column(DateTime, server_default=func.now())

    admin_profile     = relationship("AdminProfile", back_populates="user", uselist=False)
    seller_profile    = relationship("SellerProfile", back_populates="user", uselist=False)

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_seller(self):
        return self.role in {"admin", "seller"}

    @property
    def wants_to_be_seller(self):
        return self.seller_status == "pending"

    def __repr__(self):
        return (
            f"<User id={self.user_id} username={self.username!r} "
            f"role={self.role!r} seller_status={self.seller_status!r}>"
        )


class Order(Base):
    __tablename__ = "orders"

    order_id   = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    total      = Column(Numeric(10, 2), nullable=False)
    status     = Column(String(30), nullable=False, default="pending")
    created_at = Column(DateTime, server_default=func.now())

    items = relationship("OrderItem", back_populates="order")
    user  = relationship("User")

    def __repr__(self):
        return f"<Order id={self.order_id} total={self.total} status={self.status!r}>"


class OrderItem(Base):
    __tablename__ = "order_items"

    item_id       = Column(Integer, primary_key=True, autoincrement=True)
    order_id      = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    product_id    = Column(Integer, ForeignKey("products.product_id"), nullable=True)
    product_name  = Column(String(120), nullable=False)
    product_price = Column(Numeric(10, 2), nullable=False)
    quantity      = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")

    def __repr__(self):
        return f"<OrderItem order={self.order_id} product={self.product_name!r} qty={self.quantity}>"
