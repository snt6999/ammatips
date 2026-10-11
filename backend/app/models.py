from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Product(Base):
    __tablename__ = "products"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    title: Mapped[str] = mapped_column(String(240))
    subtitle: Mapped[str] = mapped_column(String(400), default="")
    category: Mapped[str] = mapped_column(String(80), default="General")
    price: Mapped[float] = mapped_column(Float)
    oldPrice: Mapped[float] = mapped_column(Float, default=0)
    emoji: Mapped[str] = mapped_column(String(30), default="📘")
    color: Mapped[str] = mapped_column(String(30), default="peach")
    description: Mapped[str] = mapped_column(Text, default="")
    features: Mapped[list] = mapped_column(JSON, default=list)
    featured: Mapped[bool] = mapped_column(default=False)
    active: Mapped[bool] = mapped_column(default=True)

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    customer_name: Mapped[str] = mapped_column(String(180))
    phone: Mapped[str] = mapped_column(String(40))
    email: Mapped[str | None] = mapped_column(String(240), nullable=True)
    transaction_id: Mapped[str] = mapped_column(String(180), index=True)
    note: Mapped[str] = mapped_column(Text, default="")
    items: Mapped[list] = mapped_column(JSON, default=list)
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(30), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
