import json
import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import database
from tutor_engine import MathTutorEngine

app = FastAPI()

# Inicializa as tabelas (questoes e interacoes)
database.init_db()

load_dotenv()
CHAVE_API = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
engine = MathTutorEngine(CHAVE_API)


# --- MODELOS DE DADOS (SCHEMAS) ---

class QuestaoSchema(BaseModel):
    enunciado: str
    url_imagem: Optional[str] = None
    link_externo: Optional[str] = None


class InteracaoSchema(BaseModel):
    sessao_id: str
    questao_id: int
    mensagem: str


# --- ROTAS DO PROFESSOR ---

@app.post("/professor/cadastrar")
async def cadastrar(data: QuestaoSchema):
    try:
        qid = database.cadastrar_questao(
            enunciado=data.enunciado,
            url_imagem=data.url_imagem,
            link_externo=data.link_externo
        )
        return {"status": "ok", "id": qid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- ROTAS DO ALUNO ---

@app.get("/questao/{qid}")
async def buscar_questao(qid: int):
    questao = database.obter_questao(qid)
    if questao:
        return dict(questao)
    raise HTTPException(status_code=404, detail="Questão não encontrada")


@app.post("/aluno/enviar")
async def aluno_enviar(data: InteracaoSchema):
    # 1. Busca o enunciado original no banco pelo ID
    questao = database.obter_questao(data.questao_id)
    if not questao:
        raise HTTPException(status_code=404, detail="Questão inexistente")

    enunciado = questao["enunciado"]

    # 2. Chamada da IA
    try:
        resposta_gerador = engine.analisar_resposta_stream(
            questao_enunciado=enunciado,
            resposta_aluno=data.mensagem
        )
        lista_resposta = list(resposta_gerador)
        resposta_json_raw = "".join(lista_resposta).strip()
        print(f"\n--- DEBUG IA RAW ---\n{resposta_json_raw}\n-------------------\n")

        # Remove formatação Markdown caso o modelo envolva em ```json ... ```
        if resposta_json_raw.startswith("```"):
            resposta_json_raw = resposta_json_raw.strip("`")
            if resposta_json_raw.startswith("json"):
                resposta_json_raw = resposta_json_raw[4:].strip()

        # Converte a string JSON em dicionário
        dados_ia = json.loads(resposta_json_raw)

        mensagem_aluno = dados_ia.get("aluno", {}).get("mensagem_socratica", "")
        diag_professor = dados_ia.get("professor", {})

    except Exception as e:
        print(f"⚠️ Erro ao processar JSON da IA: {e}")
        # Fallback de segurança: se a IA não retornar JSON, salva o texto como resposta do tutor
        mensagem_aluno = resposta_json_raw if 'resposta_json_raw' in locals() else "Desculpe, tive um problema ao processar sua resposta."
        diag_professor = {
            "categoria_radatz": "Não identificado",
            "termo_didatico": "Erro de Processamento",
            "evidencia_erro": "A resposta da IA não veio no formato JSON esperado.",
            "sugestao_intervencao": "Verifique os logs da API."
        }

    # 3. Salva no Banco de Dados (agora roda com garantia!)
    status_resp = dados_ia.get("status_resposta", "incorreta")

    database.salvar_interacao(
        sessao_id=data.sessao_id,
        questao_id=data.questao_id,
        entrada=data.mensagem,
        diag=diag_professor,
        resposta=mensagem_aluno,
        status_resposta=status_resp  # <-- passa a flag de acerto/erro
    )

    return {
        "resposta_tutor": mensagem_aluno,
        "diagnostico_interno": diag_professor
    }