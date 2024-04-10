import requests
from bs4 import BeautifulSoup
from ..config import settings
from ..utils import get_asin


scraper_url = "https://api.scraperapi.com"


def get_product_data(url: str):
    # domain = get_domain(url)
    # if not domain:
    #     return None
    asin = get_asin(url)

    payload = {"api_key": f"{settings.api_key.get_secret_value()}", "url": f"{url}"}
    response = requests.get(scraper_url, params=payload)

    soup = BeautifulSoup(response.content, "html.parser")

    product_tag_title = soup.find("span", id="productTitle")
    if product_tag_title:
        product_title = product_tag_title.string.strip()
    else:
        product_title = None
        return None

    product_current_price_tag = soup.find("span", class_="a-price-whole")
    if product_current_price_tag:
        product_current_price = "₹" + product_current_price_tag.get_text().strip(".")
    else:
        product_current_price = None

    parent_product_previous_price_tag = soup.find("span", class_="a-price a-text-price")
    if parent_product_previous_price_tag:
        product_previous_price_tag = parent_product_previous_price_tag.find(
            "span", class_="a-offscreen"
        )
        if product_previous_price_tag:
            product_previous_price = product_previous_price_tag.get_text().strip(".")
        else:
            product_previous_price = product_current_price
    else:
        product_previous_price = product_current_price

    product_discount = None
    if parent_product_previous_price_tag:
        product_discount_tag = soup.find(
            "span",
            class_="a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage",
        )
        if product_discount_tag:
            product_discount = product_discount_tag.string.strip("-")
        else:
            product_discount = None
    else:
        product_discount_tag = None

    product_ratings_count_tag = soup.find("span", id="acrCustomerReviewText")
    if product_ratings_count_tag:
        product_ratings_count = product_ratings_count_tag.string.strip()
    else:
        product_ratings_count = None

    star_rating_classes = [
        "a-icon a-icon-star a-star-4-5 cm-cr-review-stars-spacing-big",
        "a-icon a-icon-star a-star-4 cm-cr-review-stars-spacing-big",
        "a-icon a-icon-star a-star-3-5 cm-cr-review-stars-spacing-big",
        "a-icon a-icon-star a-star-3 cm-cr-review-stars-spacing-big",
        "a-icon a-icon-star a-star-5 cm-cr-review-stars-spacing-big",
        "a-icon a-icon-star a-star-2-5 cm-cr-review-stars-spacing-big",
        "a-icon a-icon-star a-star-2 cm-cr-review-stars-spacing-big",
        "a-icon a-icon-star a-star-1 cm-cr-review-stars-spacing-big",
    ]

    product_star_ratings = None
    for star_rating_class in star_rating_classes:

        parent_product_star_ratings_tag = soup.find("i", class_=star_rating_class)
        if parent_product_star_ratings_tag:
            product_star_ratings_tag = parent_product_star_ratings_tag.find(
                "span", class_="a-icon-alt"
            )
            if product_star_ratings_tag:
                product_star_ratings = product_star_ratings_tag.string.strip()
                break

    description_classes = [
        "a-unordered-list a-vertical a-spacing-mini",
        "a-unordered-list a-vertical a-spacing-small",
    ]
    product_description = []
    for description_class in description_classes:
        # product_description_ul_tag = soup.find_all("ul", class_=description_class)
        # if product_description_ul_tag:
        #     product_description_li_tags = product_description_ul_tag.find_all("li")
        #     for li in product_description_li_tags:
        #         product_description.append(li.text.strip())
        for css_class in soup.find_all("ul", class_=description_class):
            product_description_li_tags = css_class.find_all("li")
            for li in product_description_li_tags:
                product_description.append(li.text.strip())

    product_image_tags = soup.find_all(
        "img", class_=["a-dynamic-image", "a-stretch-vertical"]
    )
    for tag in product_image_tags:
        if tag and "data-old-hires" in tag.attrs:
            product_image_link = tag["data-old-hires"]

    # print(
    #     product_title,
    #     product_current_price,
    #     product_previous_price,
    #     product_discount,
    #     product_ratings_count,
    #     product_star_ratings,
    #     product_description,
    #     product_image_link,
    # )

    product_data = {
        "asin": asin,
        "title": product_title,
        "current_price": product_current_price,
        "previous_price": product_previous_price,
        "discount": product_discount,
        "ratings_count": product_ratings_count,
        "star_ratings": product_star_ratings,
        "description": product_description,
        "image_link": product_image_link,
    }

    return product_data
