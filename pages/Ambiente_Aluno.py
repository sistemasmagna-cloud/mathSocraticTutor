import streamlit as st
import requests
import os

# Configuração da página para focar no Chat
st.set_page_config(page_title="MATH-SENSE: Área do Aluno", layout="centered")

API_URL = "http://127.0.0.1:8000"

# 1. CAPTURA DO ID DA QUESTÃO VIA URL
# Exemplo de URL: http://localhost:8501/?id_questao=5
query_params = st.query_params
id_questao = query_params.get("id_questao")

if not id_questao:
    st.warning("⚠️ Por favor, acesse através do QR Code fornecido pelo seu professor.")
    st.stop()


# 2. BUSCA OS DADOS DA QUESTÃO NO BACKEND
@st.cache_data(show_spinner="Carregando o desafio...")
def carregar_dados_questao(qid):
    try:
        res = requests.get(f"{API_URL}/questao/{qid}")
        if res.status_code == 200:
            return res.json()
    except:
        return None
    return None


dados_questao = carregar_dados_questao(id_questao)

if not dados_questao:
    st.error("Desafio não encontrado. Verifique o link ou fale com o professor.")
    st.stop()

# 3. INTERFACE DE EXIBIÇÃO DO PROBLEMA
st.title("✍️ Desafio de Matemática")

with st.expander("Ver Enunciado Completo", expanded=True):
    st.markdown(f"### {dados_questao['enunciado']}")

    # Exibição da Imagem Auxiliar (se houver)
    if dados_questao.get('url_imagem'):
        nome_arquivo = dados_questao['url_imagem']

        # SOLUÇÃO: Caminho direto a partir da raiz, sem ".."
        # O os.path.join garante que a barra seja correta (\ no Windows, / no Linux)
        caminho_img = os.path.join("uploads", nome_arquivo)

        # Converter para caminho absoluto para não haver dúvida
        caminho_absoluto = os.path.abspath(caminho_img)

        if os.path.exists(caminho_absoluto):
            st.image(caminho_absoluto, use_container_width=True, caption="Figura auxiliar")
        else:
            st.error(f"Imagem não encontrada no servidor: {caminho_absoluto}")

    # Link Externo (se houver)
    if dados_questao.get('link_externo'):
        st.link_button("Abrir material de apoio", dados_questao['link_externo'])

st.divider()

# 4. LÓGICA DO CHAT SOCRÁTICO
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Mensagem inicial de boas-vindas
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Olá! Sou seu tutor socrático. Como você pretende começar a resolver esse problema?"
    })

# Exibe o histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input do Aluno
if prompt := st.chat_input("Escreva seu raciocínio aqui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chamada para o Tutor (API)
    with st.chat_message("assistant"):
        try:
            # Enviamos o id_questao para que o banco registre corretamente
            payload = {
                "sessao_id": f"aluno_{id_questao}",
                "questao_id": id_questao,
                "mensagem": prompt
            }
            res = requests.post(f"{API_URL}/aluno/enviar", json=payload)

            if res.status_code == 200:
                data = res.json()
                resposta_tutor = data["resposta_tutor"]

                # Log discreto para pesquisa (opcional)
                diag = data.get("diagnostico", {})
                st.caption(f"💡 Dica pedagógica aplicada: {diag.get('tipo_erro', 'geral')}")

                st.markdown(resposta_tutor)
                st.session_state.messages.append({"role": "assistant", "content": resposta_tutor})
            else:
                st.error("O tutor está pensando... tente novamente em instantes.")
        except Exception as e:
            st.error("Erro de conexão com o tutor.")