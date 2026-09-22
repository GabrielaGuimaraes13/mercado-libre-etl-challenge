from src.extract import (
    extract_products,
    is_target_product,
    extract_product_items,
    extract_currency_rate,
)


def main():
    print("Testando busca de produtos...")
    products = extract_products()
    print(f"Produtos encontrados: {len(products)}")

    target_products = [
        product
        for product in products
        if is_target_product(product)
    ]

    print(f"Produtos do modelo selecionado: {len(target_products)}")

    if target_products:
        first_product = target_products[0]

        print("\nExemplo de produto:")
        print(f"ID: {first_product.get('id')}")
        print(f"Nome: {first_product.get('name')}")

        print("\nTestando publicações do produto...")
        publications = extract_product_items(first_product["id"])
        print(f"Publicações encontradas: {len(publications)}")

    print("\nTestando conversão ARS -> USD...")
    currency_rate = extract_currency_rate()
    print(f"Taxa: {currency_rate.get('rate')}")

    print("\nTestes finalizados.")


if __name__ == "__main__":
    main()