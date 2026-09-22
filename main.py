from src.extract import extract_data
from src.transform import transform_data
from src.load import load_data


def main():
    print("Iniciando ETL...")

    print("Extraindo dados do Mercado Libre...")
    raw_data = extract_data()

    print(
        f"{len(raw_data['search_results'])} produtos encontrados na busca."
    )

    print(
        f"{len(raw_data['products'])} produtos correspondem ao modelo selecionado."
    )

    print(
        f"{len(raw_data['publications'])} publicações novas encontradas."
    )

    print("Transformando dados...")
    transformed_data = transform_data(raw_data)

    print(f"{len(transformed_data)} registros transformados.")

    print("Carregando dados no PostgreSQL...")
    load_data(transformed_data)

    print("ETL finalizada com sucesso.")


if __name__ == "__main__":
    main()