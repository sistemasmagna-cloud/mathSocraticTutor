from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import database
from tutor_engine import MathTutorEngine
import os
from dotenv import load_dotenv

app = FastAPI()

# Inicializa as tabelas (questoes e interacoes)
database.init_db()

load_dotenv()
CHAVE_API = os.getenv("GOOGLE_API_KEY")

engine = MathTutorEngine(CHAVE_API)


# --- MODELOS DE DADOS (SCHEMAS) ---

class QuestaoSchema(BaseModel):
    enunciado: str
    url_imagem: Optional[str] = None
    link_externo: Optional[str] = None


class InteracaoSchema(BaseModel):
    sessao_id: str
    questao_id: int  # Agora vinculamos ao ID da questão
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
        # Converte a linha do SQLite para dicionário
        return dict(questao)
    raise HTTPException(status_code=404, detail="Questão não encontrada")


@app.post("/aluno/enviar")
async def aluno_enviar(data: InteracaoSchema):
    # 1. Busca o enunciado original no banco pelo ID
    questao = database.obter_questao(data.questao_id)
    if not questao:
        raise HTTPException(status_code=404, detail="Questão inexistente")

    enunciado = questao["enunciado"]

    # 2. IA: Diagnóstico de Erro
    diag = engine.analisar_erro(enunciado, data.mensagem)

    # 3. IA: Resposta Socrática
    resposta = engine.gerar_resposta(data.sessao_id, enunciado, data.mensagem, diag)

    # 4. Banco de Dados: Salva a interação vinculada à questão
    database.salvar_interacao(
        sessao_id=data.sessao_id,
        questao_id=data.questao_id,
        entrada=data.mensagem,
        diag=diag,
        resposta=resposta
    )

    return {"resposta_tutor": resposta, "diagnostico": diag}