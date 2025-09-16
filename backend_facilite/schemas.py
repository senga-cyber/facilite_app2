# backend_facilite/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
from enum import Enum

# -----------------------
# ENUMS
# -----------------------
class RoleEnum(str, Enum):
    client = "client"
    restaurant_manager = "restaurant_manager"
    hotel_manager = "hotel_manager"
    admin = "admin"


# -----------------------
# UTILISATEURS
# -----------------------
class UserBase(BaseModel):
    name: str
    phone_number: str  # ✅ requis pour la route de login
    role: RoleEnum = RoleEnum.client  # Par défaut, le rôle est "client"


class UserCreate(UserBase):
    password: str

class UserReponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# -----------------------
# AUTH / LOGIN
# -----------------------
class ClientLogin(BaseModel):
    phone: str
# -----------------------
# MANAGERS  (ADMIN ONLY)
# -----------------------
class ManagerCreate(UserBase):
    username: str
    phone_number: str 
    email: EmailStr
    password: str
    role: RoleEnum

class ManagerLogin(BaseModel):
    phone: str
    password: str


# -----------------------
# RESTAURANTS
# -----------------------
class RestaurantBase(BaseModel):
    name: str
    adress: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = None

class RestaurantCreate(RestaurantBase):
    manager_id: int

class RestaurantResponse(RestaurantBase):
    id: int
    owner_id: int

    class Config:
       from_attributes = True



# -----------------------
# MENUS
# -----------------------
class MenuBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class MenuCreate(MenuBase):
    pass

class MenuResponse(MenuBase):
    id: int
    restaurant_id: int

    class Config:
        from_attributes = True



# -----------------------
# COMMANDES
# -----------------------
class OrderItemBase(BaseModel):
    menu_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    menu: MenuResponse

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    restaurant_id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    items: List[OrderItemCreate]

class OrderCreate(OrderBase):
    pass

class OrderResponse(BaseModel):
    id: int
    restaurant_id: int
    total: float
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True


# -----------------------
# PAIEMENTS
# -----------------------
# -----------------------
# PAIEMENTS
# -----------------------


class PaymentCreate(BaseModel):
    order_id: Optional[int] = None
    reservation_id: Optional[int] = None
    amount: float
    payment_method: str


class PaymentOut(BaseModel):
    id: int
    user_id: int
    order_id: Optional[int]
    reservation_id: Optional[int]
    amount: float
    net_amount: float
    commission: float
    payment_method: str
    status: str
    transaction_code: Optional[str]
    created_at: datetime
    qr_url: Optional[str] = None   # ✅ nouveau champ pour exposer l’URL publique du QR code

    class Config:
        from_attributes = True


# -----------------------
# HOTELS
# -----------------------
class HotelBase(BaseModel):
    name: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = None

class HotelCreate(HotelBase):
    manager_id: int

class HotelUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = None

class HotelResponse(HotelBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True



# -----------------------
# ROOMS
# -----------------------
class RoomBase(BaseModel):
    room_number: str
    type: int
    price_per_night: float
    is_available: bool=True

class RoomCreate(RoomBase):
    hotel_id: int

class RoomReponse(RoomBase):
    id: int
    hotel_id: int

    class Config:
        from_attributes = True


# -----------------------
# RÉSERVATIONS
# -----------------------
class ReservationCreate(BaseModel):
    hotel_id: int
    check_in: datetime
    check_out: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ReservationOut(ReservationCreate):
    id: int
    user_id: int
    total_price: float

    class Config:
        from_attributes = True
