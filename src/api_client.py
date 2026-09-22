import os

import requests
from dotenv import load_dotenv

from config import BASE_URL


load_dotenv()


def get_access_token():
    token = os.getenv("ML_ACCESS_TOKEN")

    if not token:
        raise ValueError("ML_ACCESS_TOKEN não encontrado no arquivo .env")

    return token


def get(endpoint, params=None):
    url = f"{BASE_URL}{endpoint}"

    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Accept": "application/json",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30,
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout as error:
        raise RuntimeError(
            f"Timeout ao acessar {endpoint}"
        ) from error

    except requests.exceptions.HTTPError as error:
        status = response.status_code

        if status == 401:
            raise RuntimeError(
                "Token inválido ou expirado. Gere um novo access token."
            ) from error

        if status == 403:
            raise RuntimeError(
                f"Acesso negado pela API no endpoint {endpoint}."
            ) from error

        raise RuntimeError(
            f"Erro {status} ao acessar {endpoint}: {response.text}"
        ) from error

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Erro de conexão com a API: {error}"
        ) from error