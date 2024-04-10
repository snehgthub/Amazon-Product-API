from datetime import datetime
from pydantic import EmailStr
from sqlmodel import Field, AutoString, SQLModel


class ProductBase(SQLModel):
    asin: str
    title: str
    current_price: str
    previous_price: str | None
    discount: str | None
    ratings_count: str | None
    star_ratings: str | None
    description: list | None
    image_link: str | None


class ProductUrl(SQLModel):
    url: str


class ProductRead(ProductBase):
    first_fetch_at: datetime


class ProductOut(ProductRead):
    id: int


class ProductASIN(SQLModel):
    asin: str


class ProductTitle(SQLModel):
    title: str


class ProductCurrentPrice(SQLModel):
    current_price: str | None


class ProductPreviousPrice(SQLModel):
    previous_price: str | None


class ProductDiscount(SQLModel):
    discount: str | None


class ProductRatingsCount(SQLModel):
    ratings_count: str | None


class ProductStarRatings(SQLModel):
    star_ratings: str | None


class ProductDescription(SQLModel):
    description: list | None


class ProductImage(SQLModel):
    image_link: str | None


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, sa_type=AutoString)


class UserCreate(UserBase):
    password: str


class UserRead(SQLModel):
    id: int
    email: EmailStr
    created_at: datetime


class UserUpdate(SQLModel):
    id: int | None = None
    email: EmailStr | None = None
    password: str | None = None


class UserLogin(SQLModel):
    email: EmailStr
    password: str


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    id: str | None = None
