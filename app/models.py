import pytz
from datetime import datetime
from sqlalchemy import JSON, TIMESTAMP, Column, ForeignKey, String, func
from sqlmodel import Field, Relationship
from typing import Optional
from .schemas import ProductBase, UserBase


class User(UserBase, table=True):
    hashed_password: str = Field()
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
        ),
        default=datetime.now(pytz.timezone("Asia/Kolkata")),
    )
    products: list["Product"] = Relationship(back_populates="user")


class Product(ProductBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    asin: str | None = Field(default=None, index=True)
    description: Optional[list] = Field(default=None, sa_type=JSON)
    image_link: Optional[str] = Field(sa_type=String, default=None)
    first_fetch_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
        ),
    )
    url: str = Field(sa_type=String)
    user_id: int = Field(
        sa_column=Column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    )
    user: User = Relationship(back_populates="products")
