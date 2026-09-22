import os

import requests
from dotenv import load_dotenv, set_key


load_dotenv()

client_id = os.getenv("ML_CLIENT_ID")
client_secret = os.getenv("ML_CLIENT_SECRET")
redirect_uri = os.getenv("ML_REDIRECT_URI")
code = os.getenv("ML_AUTH_CODE")


required_variables = {
    "ML_CLIENT_ID": client_id,
    "ML_CLIENT_SECRET": client_secret,
    "ML_REDIRECT_URI": redirect_uri,
    "ML_AUTH_CODE": code,
}

missing_variables = [
    name
    for name, value in required_variables.items()
    if not value
]

if missing_variables:
    raise ValueError(
        "Variáveis não configuradas: "
        + ", ".join(missing_variables)
    )


url = "https://api.mercadolibre.com/oauth/token"

data = {
    "grant_type": "authorization_code",
    "client_id": client_id,
    "client_secret": client_secret,
    "code": code,
    "redirect_uri": redirect_uri,
}

headers = {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded",
}


try:
    response = requests.post(
        url,
        data=data,
        headers=headers,
        timeout=20,
    )

    response.raise_for_status()

except requests.exceptions.RequestException as error:
    raise RuntimeError(
        f"Erro ao gerar access token: {error}"
    ) from error


token_data = response.json()
access_token = token_data.get("access_token")

if not access_token:
    raise RuntimeError(
        "A API não retornou um access token."
    )


set_key(
    ".env",
    "ML_ACCESS_TOKEN",
    access_token,
)

print("Access token gerado e salvo no .env com sucesso.")