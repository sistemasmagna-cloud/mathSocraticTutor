import streamlit as st
from app.auth.oauth_client import OAuthManager

def renderizar_tela_login():
    st.markdown("### 🔑 Acesse o MathSocraticTutor")
    st.caption("Selecione o seu perfil e autentique-se com sua conta Google.")

    # 1. Seleção prévia do perfil (salva na sessão antes do OAuth)
    perfil = st.radio(
        "Você é:",
        ["Aluno", "Professor"],
        horizontal=True,
        key="radio_perfil_login"
    )
    st.session_state["perfil_selecionado"] = perfil

    st.markdown("---")

    # 2. Gera a URL do Google injetando o perfil no parâmetro 'state'
    try:
        google_url = OAuthManager.obter_url_login("google", state_extra=f"google|{perfil}")
        st.link_button("🌐 Entrar com Google", google_url, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao carregar o provedor Google: {e}")