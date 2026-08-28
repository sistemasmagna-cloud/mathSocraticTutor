import streamlit as st

def inicializar_sessao():
    """Garante que as variáveis de sessão padrão estejam ativas no Streamlit."""
    if "usuario" not in st.session_state:
        st.session_state["usuario"] = None
    if "perfil_selecionado" not in st.session_state:
        st.session_state["perfil_selecionado"] = "Aluno"

def usuario_esta_autenticado() -> bool:
    """Verifica se existe um usuário ativo na sessão."""
    return st.session_state.get("usuario") is not None

def exigir_autenticacao(perfil_requerido: str = None):
    """
    Middleware/Guardião de páginas no Streamlit.
    Impede o carregamento da página se o usuário não estiver logado 
    ou se tentar acessar uma área de outro perfil.
    """
    inicializar_sessao()
    
    if not usuario_esta_autenticado():
        st.warning("🔒 Acesso restrito! Por favor, faça login para continuar.")
        st.stop()
        
    usuario = st.session_state["usuario"]
    if perfil_requerido and usuario.get("perfil") != perfil_requerido:
        st.error(f"⛔ Acesso negado. Esta página é exclusiva para usuários com perfil de **{perfil_requerido}**.")
        st.stop()

def efetuar_logout():
    """Limpa a sessão do usuário e reinicia a aplicação."""
    st.session_state["usuario"] = None
    st.session_state.clear()
    st.rerun()