import os

import psycopg2
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    required_variables = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ]

    missing_variables = [
        variable
        for variable in required_variables
        if not os.getenv(variable)
    ]

    if missing_variables:
        raise ValueError(
            "Variáveis de banco não configuradas: "
            + ", ".join(missing_variables)
        )

    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def load_data(records):
    if not records:
        print("Nenhum registro para carregar.")
        return

    query = """
        INSERT INTO mercado_livre_items (
            item_id,
            product_id,
            product_name,
            seller_id,
            price_ars,
            exchange_rate,
            price_usd,
            sold_quantity,
            warranty,
            has_warranty,
            shipping_mode,
            logistic_type,
            free_shipping,
            condition,
            job_run
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
    """

    values = []

    for record in records:
        values.append(
            (
                record["item_id"],
                record["product_id"],
                record["product_name"],
                record["seller_id"],
                record["price_ars"],
                record["exchange_rate"],
                record["price_usd"],
                record["sold_quantity"],
                record["warranty"],
                record["has_warranty"],
                record["shipping_mode"],
                record["logistic_type"],
                record["free_shipping"],
                record["condition"],
                record["job_run"],
            )
        )

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.executemany(query, values)

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()