from contextlib import asynccontextmanager
from fastapi import FastAPI

from .database import create_db_and_tables
from .routers import (
    complete_product_info,
    image,
    asin,
    title,
    description,
    current_price,
    previous_price,
    discount,
    ratings_count,
    star_ratings,
    user,
    auth,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(complete_product_info.router)
app.include_router(asin.router)
app.include_router(title.router)
app.include_router(description.router)
app.include_router(current_price.router)
app.include_router(previous_price.router)
app.include_router(discount.router)
app.include_router(ratings_count.router)
app.include_router(star_ratings.router)
app.include_router(image.router)
app.include_router(user.router)
app.include_router(auth.router)


@app.get("/")
def homepage():
    return {"message": "Welcome to Amazon Product API!"}
