from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, or_
from ..database import engine
from .. import schemas, models, oauth2
from ..utils import get_asin, get_shortened_url
from ..scraping.scraper import get_product_data

router = APIRouter(prefix="/product", tags=["Product ASIN"])


@router.post(
    "/asin", status_code=status.HTTP_200_OK, response_model=schemas.ProductASIN
)
def get_asin_from_url(
    url: schemas.ProductUrl,
    current_user: models.User = Depends(oauth2.get_current_user),
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform the following action",
        )
    product_asin = get_asin(url.url)
    if not product_asin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cannot find ASIN: Invalid URL",
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

        product_db = session.exec(
            select(models.Product).where(models.Product.asin == product_asin)
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
