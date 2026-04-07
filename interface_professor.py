import streamlit as st
import requests
import os
from utils import gerar_imagem_qrcode  # Importando a função acima

st.set_page_config(page_title="Painel do Professor - MATH-SENSE", layout="wide")

API_URL = "http://127.0.0.1:8000"
# URL base onde a página do aluno estará hospedada (ajuste conforme seu servidor)
BASE_URL_ALUNO = "http://localhost:8501/Ambiente_Aluno?id_questao="

st.title("🍎 Painel de Gestão Pedagógica")

with st.form("form_cadastro"):
    st.subheader("Cadastrar Novo Desafio Socrático")
    enunciado = st.text_area("Enunciado do problema:", height=150)
    arquivo = st.file_uploader("Adicionar Imagem Auxiliar (opcional)", type=['png', 'jpg', 'jpeg'])
    link = st.text_input("Link de referência externa (opcional):")

    btn_enviar = st.form_submit_button("Gerar Questão e QR Code")

if btn_enviar:
    if not enunciado:
        st.error("O enunciado é obrigatório.")
    else:
        # 1. Trata a imagem
        nome_imagem = None
        if arquivo:
            nome_imagem = arquivo.name
            if not os.path.exists("uploads"): os.makedirs("uploads")
            with open(os.path.join("uploads", nome_imagem), "wb") as f:
                f.write(arquivo.getbuffer())

        # 2. Envia para o Backend
        payload = {"enunciado": enunciado, "url_imagem": nome_imagem, "link_externo": link}
        try:
            res = requests.post(f"{API_URL}/professor/cadastrar", json=payload)
            if res.status_code == 200:
                id_questao = res.json()["id"]
                st.success(f"Questão #{id_questao} cadastrada com sucesso!")

                # 3. Gera o QR Code com o link dinâmico
                url_final = f"{BASE_URL_ALUNO}{id_questao}"
                img_qr = gerar_imagem_qrcode(url_final)

                # 4. Exibe os resultados
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Link Direto:**")
                    st.code(url_final)
                    st.image(img_qr, caption="QR Code para os Alunos", width=300)
                with col2:
                    st.write("**Visualização do Professor:**")
                    if arquivo: st.image(arquivo, width=250)
                    st.info(f"O Aluno verá o enunciado e poderá interagir com o tutor socrático via este link.")
        except Exception as e:
            st.error(f"Erro ao conectar com o servidor: {e}")