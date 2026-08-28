from datetime import datetime
from sqlalchemy.orm import Session
from app.models.usuario import Usuario, PerfilEnum

class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def buscar_por_email(self, email: str) -> Usuario | None:
        """Busca o usuário no banco de dados pelo e-mail (login único)."""
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def criar_ou_atualizar(
        self, 
        email: str, 
        nome: str, 
        foto: str | None, 
        provedor: str, 
        provider_id: str, 
        perfil_selecionado: PerfilEnum
    ) -> Usuario:
        """
        Cria um novo usuário salvando o perfil escolhido (Professor/Aluno)
        ou apenas atualiza a data do último acesso caso já esteja cadastrado.
        """
        usuario = self.buscar_por_email(email)

        if usuario:
            # Usuário existente: apenas atualiza o último acesso e a foto
            usuario.last_login = datetime.utcnow()
            if foto:
                usuario.foto = foto
        else:
            # Usuário novo: insere com o perfil escolhido antes do OAuth
            usuario = Usuario(
                email=email,
                nome=nome,
                foto=foto,
                provedor=provedor,
                provider_id=provider_id,
                perfil=perfil_selecionado,
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow(),
                ativo=True
            )
            self.db.add(usuario)

        self.db.commit()
        self.db.refresh(usuario)
        return usuario