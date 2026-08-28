import os
from authlib.integrations.httpx_client import AsyncOAuth2Client
from dotenv import load_dotenv

load_dotenv()

REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8501")

PROVIDERS_CONFIG = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo",
        "scopes": ["openid", "email", "profile"]
    }
}

class OAuthManager:
    @staticmethod
    def obter_url_login(provedor: str = "google", state_extra: str = "") -> str:
        """
        Gera a URL de login do Google. 
        O parâmetro 'state_extra' carrega o perfil escolhido (ex: 'google|Professor').
        """
        config = PROVIDERS_CONFIG.get(provedor)
        if not config:
            raise ValueError(f"Provedor {provedor} não configurado ou não suportado.")

        if not config["client_id"] or not config["client_secret"]:
            raise ValueError(f"Credenciais para o provedor {provedor} não foram encontradas no .env")

        client = AsyncOAuth2Client(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            scope=" ".join(config["scopes"]),
            redirect_uri=REDIRECT_URI
        )

        uri, state = client.create_authorization_url(
            config["authorize_url"],
            state=state_extra
        )
        return uri