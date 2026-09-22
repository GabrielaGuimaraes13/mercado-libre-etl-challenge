-- 1. Vendedores com múltiplas publicações

SELECT
    seller_id,
    COUNT(*) AS publications
FROM mercado_livre_items
WHERE job_run = (
    SELECT MAX(job_run)
    FROM mercado_livre_items
)
GROUP BY seller_id
HAVING COUNT(*) > 1
ORDER BY publications DESC;


-- 2. Média de vendas por vendedor
-- sold_quantity ficou NULL nesta execução porque
-- o acesso aos detalhes dos itens retornou HTTP 403.

SELECT
    seller_id,
    ROUND(AVG(sold_quantity), 2) AS average_sales
FROM mercado_livre_items
WHERE job_run = (
    SELECT MAX(job_run)
    FROM mercado_livre_items
)
AND sold_quantity IS NOT NULL
GROUP BY seller_id
ORDER BY average_sales DESC;


-- 3. Preço médio em USD

SELECT
    ROUND(AVG(price_usd), 2) AS average_price_usd
FROM mercado_livre_items
WHERE job_run = (
    SELECT MAX(job_run)
    FROM mercado_livre_items
);


-- 4. Percentual de publicações com garantia

SELECT
    COUNT(*) AS total_items,
    COUNT(*) FILTER (
        WHERE has_warranty = TRUE
    ) AS items_with_warranty,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE has_warranty = TRUE
        ) / COUNT(*),
        2
    ) AS warranty_percentage
FROM mercado_livre_items
WHERE job_run = (
    SELECT MAX(job_run)
    FROM mercado_livre_items
);


-- 5. Métodos de envio

SELECT
    shipping_mode,
    logistic_type,
    COUNT(*) AS publications
FROM mercado_livre_items
WHERE job_run = (
    SELECT MAX(job_run)
    FROM mercado_livre_items
)
GROUP BY
    shipping_mode,
    logistic_type
ORDER BY publications DESC;