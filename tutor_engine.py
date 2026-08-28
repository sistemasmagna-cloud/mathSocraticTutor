import json
import os
from google import genai
from google.genai import types

SYSTEM_INSTRUCTION = """
Você é o MathSocraticTutor, um assistente pedagógico inteligente para o ensino de Matemática baseado na Teoria das Situações Didáticas (Brousseau) e na Análise de Erros (Radatz).

Sua tarefa é analisar a resposta fornecida pelo aluno e responder ESTRITAMENTE em formato JSON.
NUNCA adicione textos fora do JSON, como "💡 Dica pedagógica", explicações ou marcadores markdown extras.

--- FORMATO DE SAÍDA OBRIGATÓRIO (JSON) ---
{
  "status_resposta": "incorreta",
  "aluno": {
    "mensagem_socratica": "Pergunta ou provocação didática direcionada ao aluno."
  },
  "professor": {
    "categoria_radatz": "Associações Deficientes",
    "termo_didatico": "Confusão de Conceitos",
    "evidencia_erro": "O aluno usou a operação de subtração em vez de adição para representar o aumento no comprimento.",
    "sugestao_intervencao": "Peça para o aluno destacar a palavra 'aumentado' no enunciado e associar ao sinal matemático correto."
  }
}

--- REGRAS PARA O ALUNO ---
- NÃO dê a resposta pronta nem revele a fórmula final.
- Faça uma pergunta investigativa (socrática) para que ele perceba o erro por conta própria.

--- REGRAS PARA O PROFESSOR ---
- Categorias de Radatz x Termo Didático:
  * Dificuldade de Linguagem -> "Interpretação de Texto / Vocabulário"
  * Processamento Espacial -> "Raciocínio Visual / Geométrico"
  * Associações Deficientes -> "Confusão de Conceitos ou Fórmulas"
  * Regras Irrelevantes -> "Uso de Macetes / Aplicação Incorreta de Regra"
  * Erro de Execução -> "Cálculo Básico ou Digitação"
  * Nenhum Erro -> "Compreensão Adequada"
"""


class MathTutorEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("API Key do Gemini não foi encontrada.")

        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.5-flash"

    def analisar_resposta_stream(self, questao_enunciado: str, resposta_aluno: str):
        prompt_usuario = f"""
        [ENUNCIADO DA QUESTÃO]:
        {questao_enunciado}

        [RESPOSTA SUBMETIDA PELO ALUNO]:
        {resposta_aluno}

        Retorne o diagnóstico do PROFESSOR e a mediação para o ALUNO exclusivamente no formato JSON especificado.
        """

        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            temperature=0.1  # Temperatura baixa para garantir adesão ao formato JSON
        )

        response_stream = self.client.models.generate_content_stream(
            model=self.model_name,
            contents=prompt_usuario,
            config=config
        )

        for chunk in response_stream:
            if chunk.text:
                yield chunk.text