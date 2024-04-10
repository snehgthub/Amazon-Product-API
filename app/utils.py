import re
from .config import settings
import requests
from passlib.context import CryptContext
from . import models

DOMAIN_NAMES = ["amazon", "amzn"]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_domain(url: str):
    try:
        domain_name = url.split("/")[2][::-1].split(".")[1][::-1]

        if domain_name in DOMAIN_NAMES:
            return domain_name
        else:
            return None

    except IndexError:
        return None


def extract_asin(url: str):
    asinPattern = r"/([A-Z0-9]{10})(?:[/?]|$)"

    match = re.search(asinPattern, url)

    if match:
        return match.group(1)
    else:
        return None


def get_asin(url: str):
    domain_name = get_domain(url)
    if domain_name == DOMAIN_NAMES[0]:
        product_asin = extract_asin(url)

    elif domain_name == DOMAIN_NAMES[1]:
        payload = {"api_key": f"{settings.api_key.get_secret_value()}", "url": url}

        scraper_url = "http://api.scraperapi.com"

        response = requests.get(scraper_url, params=payload, allow_redirects=True)
        if response.status_code == 200:
            redirect_url = response.headers["sa-final-url"]
            product_asin = extract_asin(redirect_url)
        else:
            return None

    return product_asin


def product_exists(url: str):
    domain = get_domain(url)
    if not domain:
        return None

    product_asin = get_asin(url)
    if not product_asin:
        return None

    return product_asin


def get_shortened_url(url: str):
    if "amzn" in url:
        return url
    else:
        match = re.search(r"/dp/([A-Z0-9]{10})", url)
        if match:
            desired_url = url[: match.end()] + "/"

        return desired_url


def clone_product_for_user(product_db, new_user_id):
    new_product = models.Product(
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
        user_id=new_user_id,
    )
    return new_product


def create_new_product(product_data, user_id, url):
    new_product = models.Product(
        asin=product_data["asin"],
        title=product_data["title"],
        current_price=product_data["current_price"],
        previous_price=product_data["previous_price"],
        discount=product_data["discount"],
        star_ratings=product_data["star_ratings"],
        ratings_count=product_data["ratings_count"],
        description=product_data["description"],
        image_link=product_data["image_link"],
        url=get_shortened_url(url),
        user_id=user_id,
    )
    return new_product
