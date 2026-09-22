CREATE TABLE IF NOT EXISTS mercado_livre_items (
    item_id VARCHAR(30) NOT NULL,
    product_id VARCHAR(30) NOT NULL,
    product_name TEXT,
    seller_id BIGINT NOT NULL,

    price_ars NUMERIC(14, 2),
    exchange_rate NUMERIC(15, 8),
    price_usd NUMERIC(14, 2),

    sold_quantity INTEGER,

    warranty TEXT,
    has_warranty BOOLEAN,

    shipping_mode VARCHAR(50),
    logistic_type VARCHAR(50),
    free_shipping BOOLEAN,

    condition VARCHAR(20),

    job_run TIMESTAMP NOT NULL,

    PRIMARY KEY (item_id, job_run)
);