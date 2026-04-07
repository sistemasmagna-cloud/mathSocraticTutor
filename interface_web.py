import streamlit as st
import requests

# Configurações da página
st.set_page_config(page_title="MATH-SENSE: Tutor Socrático", layout="centered")

API_URL = "http://127.0.0.1:8000"

st.title("🎓 Projeto MATH-SENSE")
st.subheader("Mediação Socrática com IA")

# Criando as abas de navegação
aba_prof, aba_aluno = st.tabs(["🍎 Área do Professor", "✍️ Área do Aluno"])

# --- ABA DO PROFESSOR ---
with aba_prof:
    st.write("### Configuração da Atividade")
    enunciado = st.text_area("Digite o problema matemático para a turma:")
    if st.button("Definir Enunciado"):
        try:
            res = requests.post(f"{API_URL}/professor/configurar", json={"texto": enunciado})
            if res.status_code == 200:
                st.success("Enunciado enviado com sucesso para o Backend!")
        except:
            st.error("Erro: Verifique se a sua API (Uvicorn) está rodando!")

# --- ABA DO ALUNO ---
with aba_aluno:
    st.write("### Chat com o Tutor")

    # Inicializa o histórico de chat na interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Exibe mensagens anteriores
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input do aluno
    if prompt := st.chat_input("Sua resposta ou dúvida..."):
        # Mostra a mensagem do aluno
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Chama a API
        with st.chat_message("assistant"):
            try:
                res = requests.post(
                    f"{API_URL}/aluno/enviar",
                    json={"sessao_id": "aluno_web_01", "mensagem": prompt}
                )
                resposta_json = res.json()
                texto_tutor = resposta_json["resposta_tutor"]

                # Exibe o diagnóstico técnico de forma discreta para o pesquisador
                diag = resposta_json["diagnostico"]
                st.caption(f"🔍 [Pesquisa] Erro detectado: {diag['tipo_erro']} | Conceito: {diag['conceito']}")

                st.markdown(texto_tutor)
                st.session_state.messages.append({"role": "assistant", "content": texto_tutor})
            except:
                st.error("Ocorreu um erro ao falar com o tutor.")