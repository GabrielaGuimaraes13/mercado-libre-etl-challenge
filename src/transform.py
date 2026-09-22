from datetime import datetime


def has_warranty(warranty):
    return bool(warranty and warranty.strip())


def transform_publications(publications, currency_rate, job_run):
    transformed = []

    rate = currency_rate["rate"]

    for publication in publications:
        shipping = publication.get("shipping") or {}

        price_ars = publication.get("price")
        price_usd = None

        if price_ars is not None:
            price_usd = round(price_ars * rate, 2)

        transformed.append(
            {
                "item_id": publication.get("item_id"),
                "product_id": publication.get("product_id"),
                "product_name": publication.get("product_name"),
                "seller_id": publication.get("seller_id"),
                "price_ars": price_ars,
                "exchange_rate": rate,
                "price_usd": price_usd,

                # Item details returned HTTP 403 during extraction.
                # NULL is used instead of zero to avoid creating
                # an incorrect sales value.
                "sold_quantity": None,

                "warranty": publication.get("warranty"),
                "has_warranty": has_warranty(
                    publication.get("warranty")
                ),
                "shipping_mode": shipping.get("mode"),
                "logistic_type": shipping.get("logistic_type"),
                "free_shipping": shipping.get("free_shipping"),
                "condition": publication.get("condition"),
                "job_run": job_run,
            }
        )

    return transformed


def transform_data(data):
    job_run = datetime.now()

    return transform_publications(
        publications=data["publications"],
        currency_rate=data["currency_rate"],
        job_run=job_run,
    )