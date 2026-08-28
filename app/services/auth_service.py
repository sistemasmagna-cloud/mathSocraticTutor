import httpx
from sqlalchemy.orm import Session
from app.auth.oauth_client import PROVIDERS_CONFIG, REDIRECT_URI
from app.repositories.usuario_repository import UsuarioRepository
from app.models.usuario import PerfilEnum, Usuario

class AuthService:
    def __init__(self, db: Session):
        self.repo = UsuarioRepository(db)

    async def processar_callback_oauth(self, provedor: str, code: str, perfil_escolhido: str) -> Usuario:
        """
        1. Troca o 'code' por um Access Token via Authlib/HTTPX.
        2. Recupera o e-mail e dados do perfil no endpoint do Google.
        3. Valida a confirmação do e-mail.
        4. Cria ou atualiza o registro do usuário na base de dados.
        """
        config = PROVIDERS_CONFIG.get(provedor)
        if not config:
            raise ValueError(f"Provedor {provedor} não configurado.")

        # 1. Troca do 'code' pelo Token de Acesso no Google
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                config["token_url"],
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": REDIRECT_URI,
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"]
                }
            )
            
            if token_resp.status_code != 200:
                raise ValueError("Erro ao obter token de acesso junto ao provedor.")

            token_data = token_resp.json()
            access_token = token_data.get("access_token")

            # 2. Busca dos dados básicos do usuário (OpenID Connect UserInfo)
            headers = {"Authorization": f"Bearer {access_token}"}
            user_resp = await client.get(config["userinfo_endpoint"], headers=headers)
            
            if user_resp.status_code != 200:
                raise ValueError("Erro ao obter dados do usuário no Google.")

            raw_user = user_resp.json()

        # 3. Normalização dos dados do Google + Verificação de e-mail
        if provedor == "google":
            if not raw_user.get("email_verified", False):
                raise ValueError("E-mail não verificado pelo Google. Acesso negado.")
            
            email = raw_user["email"]
            nome = raw_user.get("name", email.split("@")[0])
            foto = raw_user.get("picture")
            provider_id = raw_user["sub"]  # Identificador único OIDC
        else:
            raise ValueError(f"Provedor {provedor} não implementado.")

        # Convertemos a string do perfil recebida na UI para o Enum do SQLAlchemy
        perfil_enum = PerfilEnum.PROFESSOR if perfil_escolhido == "Professor" else PerfilEnum.ALUNO
        
        # 4. Upsert (Cria novo usuário ou atualiza último acesso)
        usuario = self.repo.criar_ou_atualizar(
            email=email,
            nome=nome,
            foto=foto,
            provedor=provedor,
            provider_id=provider_id,
            perfil_selecionado=perfil_enum
        )
        
        return usuario