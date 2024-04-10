from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, or_
from ..database import engine
from .. import schemas, models, oauth2
from ..utils import product_exists, get_shortened_url
from ..scraping.scraper import get_product_data

router = APIRouter(prefix="/product", tags=["Product Star Ratings"])


@router.post(
    "/star-ratings",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ProductStarRatings,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": schemas.HTTPError},
    },
)
def get_star_ratings_from_url(
    url: schemas.ProductUrl,
    current_user: models.User = Depends(oauth2.get_current_user),
):
    product_asin = product_exists(url.url)
    if not product_asin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cannot retrieve Star Ratings: no product found with the given URL",
        )
    with Session(engine) as session:
        # Check if the current user already has this product
        existing_user_product = session.exec(
            select(models.Product).where(
                models.Product.asin == product_asin,
                models.Product.user_id == current_user.id,
            )
        ).first()

        # If the current user already has this product, return it
        if existing_user_product:
            return existing_user_product

        # If the product exists in database but not for current user, create a new entry for the current user
        product_db = session.exec(
            select(models.Product).where(models.Product.asin == product_asin),
        ).first()

        if product_db:
            new_product_entry = models.Product(
                asin=product_db.asin,
                title=product_db.title,
                current_price=product_db.current_price,
                previous_price=product_db.previous_price,
                discount=product_db.discount,
                star_ratings=product_db.star_ratings,
                ratings_count=product_db.ratings_count,
                description=product_db.description,
                image_link=product_db.image_link,
                url=product_db.url,
                user_id=current_user.id,
            )
            session.add(new_product_entry)
            session.commit()
            session.refresh(new_product_entry)
            return new_product_entry

    product_data = get_product_data(url.url)
    product = models.Product(
        asin=product_data["asin"],
        title=product_data["title"],
        current_price=product_data["current_price"],
        previous_price=product_data["previous_price"],
        discount=product_data["discount"],
        star_ratings=product_data["star_ratings"],
        ratings_count=product_data["ratings_count"],
        description=product_data["description"],
        image_link=product_data["image_link"],
        url=get_shortened_url(url.url),
        user_id=current_user.id,
    )
    with Session(engine) as session:
        session.add(product)
        session.commit()
        session.refresh(product)
    return product


@router.get(
    "/{asin}/star-ratings",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ProductStarRatings,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": schemas.HTTPError},
    },
)
def get_star_ratings_by_asin(
    asin: str, current_user: models.User = Depends(oauth2.get_current_user)
):
    with Session(engine) as session:
        # Check if the current user already has this product
        existing_user_product = session.exec(
            select(models.Product).where(
                models.Product.asin == asin,
                models.Product.user_id == current_user.id,
            )
        ).first()

        # If the current user already has this product, return it
        if existing_user_product:
            return existing_user_product

        product_db = session.exec(
            select(models.Product).where(models.Product.asin == asin)
        ).first()
        if product_db:
            new_product_entry = models.Product(
                asin=product_db.asin,
                title=product_db.title,
                current_price=product_db.current_price,
                previous_price=product_db.previous_price,
                discount=product_db.discount,
                star_ratings=product_db.star_ratings,
                ratings_count=product_db.ratings_count,
                description=product_db.description,
                image_link=product_db.image_link,
                url=product_db.url,
                user_id=current_user.id,
            )
            session.add(new_product_entry)
            session.commit()
            session.refresh(new_product_entry)
            return new_product_entry

    url = "https://www.amazon.in/dp/" + asin

    product_data = get_product_data(url)

    if not product_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No product found with the given ASIN",
        )
    product = models.Product(
        asin=product_data["asin"],
        title=product_data["title"],
        current_price=product_data["current_price"],
        previous_price=product_data["previous_price"],
        discount=product_data["discount"],
        star_ratings=product_data["star_ratings"],
        ratings_count=product_data["ratings_count"],
        description=product_data["description"],
        image_link=product_data["image_link"],
        url=url,
        user_id=current_user.id,
    )
    with Session(engine) as session:
        session.add(product)
        session.commit()
        session.refresh(product)
    return product
