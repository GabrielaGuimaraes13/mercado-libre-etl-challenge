BASE_URL = "https://api.mercadolibre.com"

SITE_ID = "MLA"
SEARCH_QUERY = "Samsung Galaxy S24 FE"
DOMAIN_ID = "MLA-CELLPHONES"

PAGE_SIZE = 50
MAX_PRODUCTS = 100

ENDPOINTS = {
    "products": "/products/search",
    "product_items": "/products/{product_id}/items",
    "currency_conversion": "/currency_conversions/search",
}