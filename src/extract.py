from config import (
    SITE_ID,
    SEARCH_QUERY,
    DOMAIN_ID,
    PAGE_SIZE,
    MAX_PRODUCTS,
    ENDPOINTS,
)

from src.api_client import get


def extract_products():
    products = []
    offset = 0

    while len(products) < MAX_PRODUCTS:
        params = {
            "site_id": SITE_ID,
            "q": SEARCH_QUERY,
            "domain_id": DOMAIN_ID,
            "status": "active",
            "limit": PAGE_SIZE,
            "offset": offset,
        }

        data = get(ENDPOINTS["products"], params)
        results = data.get("results", [])

        if not results:
            break

        products.extend(results)

        if len(results) < PAGE_SIZE:
            break

        offset += PAGE_SIZE

    return products[:MAX_PRODUCTS]


def is_target_product(product):
    name = product.get("name", "").upper()
    normalized_name = name.replace("-", " ").replace(" ", "")

    attributes = {
        attribute.get("id"): attribute.get("value_name", "")
        for attribute in product.get("attributes", [])
    }

    brand = attributes.get("BRAND", "").upper()

    return (
        brand == "SAMSUNG"
        and "S24FE" in normalized_name
    )


def extract_product_items(product_id):
    endpoint = ENDPOINTS["product_items"].format(
        product_id=product_id
    )

    try:
        data = get(endpoint)
        return data.get("results", [])

    except RuntimeError as error:
        if "404" in str(error):
            return []

        raise


def extract_publications(products):
    publications = []

    for product in products:
        product_id = product["id"]
        items = extract_product_items(product_id)

        for item in items:
            if item.get("condition") != "new":
                continue

            item["product_id"] = product_id
            item["product_name"] = product.get("name")

            publications.append(item)

    return publications


def extract_currency_rate():
    params = {
        "from": "ARS",
        "to": "USD",
    }

    return get(
        ENDPOINTS["currency_conversion"],
        params,
    )


def extract_data():
    products = extract_products()

    target_products = [
        product
        for product in products
        if is_target_product(product)
    ]

    publications = extract_publications(target_products)
    currency_rate = extract_currency_rate()

    return {
        "search_results": products,
        "products": target_products,
        "publications": publications,
        "currency_rate": currency_rate,
    }