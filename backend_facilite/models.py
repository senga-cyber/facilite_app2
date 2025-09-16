# backend_facilite/models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum

# -----------------------
# ENUMS
# -----------------------
class RoleEnum(str, enum.Enum):
    client = "client"
    restaurant_manager = "restaurant_manager"
    hotel_manager = "hotel_manager"
    delivery_person = "delivery_person"  # ✅ nouveau rôle livreur
    admin = "admin"

class DeliveryStatusEnum(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    in_progress = "in_progress"
    delivered = "delivered"
    cancelled = "cancelled"

# -----------------------
# UTILISATEURS
# -----------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # sécurisé
    role = Column(Enum(RoleEnum), default=RoleEnum.client, nullable=False)
    email = Column(String, unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    restaurants = relationship("Restaurant", back_populates="owner")
    hotels = relationship("Hotel", back_populates="owner")
    orders = relationship("Order", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    deliveries = relationship("Delivery", back_populates="delivery_person")  # ✅ livraisons assignées

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, role={self.role})>"

# -----------------------
# RESTAURANTS
# -----------------------
class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, index=True, nullable=False)
    address = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    owner = relationship("User", back_populates="restaurants")
    menus = relationship("Menu", back_populates="restaurant")
    orders = relationship("Order", back_populates="restaurant")

    def __repr__(self):
        return f"<Restaurant(id={self.id}, name={self.name})>"

# -----------------------
# MENUS
# -----------------------
class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)  # description du plat
    category = Column(String, nullable=True)     # entrée, plat, dessert
    price = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)    # photo du plat

    restaurant = relationship("Restaurant", back_populates="menus")
    order_items = relationship("OrderItem", back_populates="menu")

    def __repr__(self):
        return f"<Menu(id={self.id}, name={self.name}, price={self.price})>"

# -----------------------
# HOTELS
# -----------------------
class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    price_per_night = Column(Float, nullable=False)

    owner = relationship("User", back_populates="hotels")
    reservations = relationship("Reservation", back_populates="hotel")
    rooms = relationship("Room", back_populates="hotel")

    def __repr__(self):
        return f"<Hotel(id={self.id}, name={self.name}, city={self.city})>"

# -----------------------
# ROOMS
# -----------------------
class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    room_number = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    price_per_night = Column(Float, nullable=False)

    hotel = relationship("Hotel", back_populates="rooms")

# -----------------------
# RESERVATIONS
# -----------------------
class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    check_in = Column(DateTime, nullable=False)
    check_out = Column(DateTime, nullable=False)
    total_price = Column(Float, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    user = relationship("User", back_populates="reservations")
    hotel = relationship("Hotel", back_populates="reservations")

# -----------------------
# COMMANDES
# -----------------------
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    total = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    items = relationship("OrderItem", back_populates="order")
    user = relationship("User", back_populates="orders")
    restaurant = relationship("Restaurant", back_populates="orders")
    delivery = relationship("Delivery", back_populates="order", uselist=False)  # ✅ 1 delivery / order

# -----------------------
# PAIEMENTS
# -----------------------
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=True)
    amount = Column(Float, nullable=False)

    # commissions: 2$ app + frais passerelle (selon méthode)
    net_amount = Column(Float, nullable=False)
    commission = Column(Float, default=1.0)

    payment_method = Column(String, default="cash")
    status = Column(String, default="pending")
    transaction_code = Column(String, unique=True, index=True, nullable=True)

    # QR
    is_used = Column(Boolean, default=False, nullable=False)
    qr_path = Column(String, nullable=True)
    discount = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="payments")
    order = relationship("Order")
    reservation = relationship("Reservation")

# -----------------------
# LIVRAISONS
# -----------------------
class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    delivery_person_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(DeliveryStatusEnum), default=DeliveryStatusEnum.pending, nullable=False)

    latitude = Column(Float, nullable=True)   # position actuelle du livreur
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relations
    order = relationship("Order", back_populates="delivery")
    delivery_person = relationship("User", back_populates="deliveries")

# -----------------------
# ORDER ITEMS
# -----------------------
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")
    menu = relationship("Menu", back_populates="order_items")
