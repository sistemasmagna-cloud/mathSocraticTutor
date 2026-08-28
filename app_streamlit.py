import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao PATH do Python antes de qualquer import do projeto
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import asyncio
import streamlit as st
from app.database.connection import init_db, SessionLocal
from app.services.auth_service import AuthService
from app.components.login_ui import renderizar_tela_login
from app.utils.session_manager import inicializar_sessao, efetuar_logout, usuario_esta_autenticado

# Configuração inicial da página Streamlit
st.set_page_config(
    page_title="MathSocraticTutor",
    page_icon="🎓",
    layout="centered"
)

# Inicializa as tabelas do SQLite (se não existirem) e a sessão
init_db()
inicializar_sessao()

# --- INTERCEPTADOR DO CALLBACK OAUTH (Query Params na URL) ---
query_params = st.query_params

if "code" in query_params and "state" in query_params and not usuario_esta_autenticado():
    code = query_params["code"]
    state = query_params["state"]  # Esperado: "google|Professor" ou "google|Aluno"
    
    try:
        provedor, perfil_escolhido = state.split("|")
        
        db = SessionLocal()
        auth_service = AuthService(db)
        
        # Processa a troca do código pelo perfil do usuário
        usuario = asyncio.run(auth_service.processar_callback_oauth(provedor, code, perfil_escolhido))
        db.close()

        # Guarda os dados do usuário autenticado no session_state do Streamlit
        st.session_state["usuario"] = {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "foto": usuario.foto,
            "perfil": usuario.perfil.value,
            "provedor": usuario.provedor
        }

        # Limpa os parâmetros de código da URL por segurança e recarrega
        st.query_params.clear()
        st.rerun()

    except Exception as e:
        st.error(f"Falha na autenticação: {str(e)}")
        st.query_params.clear()

# --- RENDERIZAÇÃO DA INTERFACE ---
if not usuario_esta_autenticado():
    renderizar_tela_login()
else:
    user = st.session_state["usuario"]
    
    # Menu na barra lateral
    with st.sidebar:
        if user.get("foto"):
            st.image(user["foto"], width=80)
        st.markdown(f"**{user['nome']}**")
        st.caption(f"📧 {user['email']}")
        st.caption(f"👤 Perfil: **{user['perfil']}**")
        
        st.markdown("---")
        if st.button("🚪 Sair (Logout)", use_container_width=True):
            efetuar_logout()

    # Área logada inicial
    st.title("🎓 Bem-vindo ao MathSocraticTutor")
    st.success(f"Autenticado com sucesso via **{user['provedor'].capitalize()}**!")
    
    st.write(f"Olá, **{user['nome']}**! Você está conectado com o perfil de **{user['perfil']}**.")
    st.info("Navegue pelas opções no menu lateral para acessar o tutor socrático ou as análises do professor.")