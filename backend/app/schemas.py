from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Optional, Any

class LoginRequest(BaseModel):
    email: str
    password: str

class ProductPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    id: Optional[str] = None
    title: str = Field(min_length=2, max_length=240)
    subtitle: str = ""
    category: str = "General"
    price: float = Field(gt=0)
    old_price: float = Field(default=0, alias="oldPrice", ge=0)
    emoji: str = "📘"
    color: str = "peach"
    description: str = ""
    features: list[str] = []
    featured: bool = False
    active: bool = True

class OrderItemRequest(BaseModel):
    product_id: str
    quantity: int = Field(default=1, ge=1, le=20)

class CreateOrderRequest(BaseModel):
    customer_name: str = Field(min_length=2, max_length=180)
    phone: str = Field(min_length=8, max_length=40)
    email: Optional[str] = None
    transaction_id: str = Field(min_length=3, max_length=180)
    note: str = ""
    items: list[OrderItemRequest] = Field(min_length=1, max_length=30)

class StatusUpdate(BaseModel):
    status: str

class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: str
    title: str
    subtitle: str
    category: str
    price: float
    oldPrice: float
    emoji: str
    color: str
    description: str
    features: list[str]
    featured: bool
    active: bool
