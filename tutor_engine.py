import json
from google import genai
from google.genai import types  # Importação essencial para evitar erros de validação

class MathTutorEngine:
    def __init__(self, api_key: str):
        # Inicializa o cliente normalmente
        self.client = genai.Client(
            api_key=api_key,
            http_options={'api_version': 'v1'}
        )
        self.model_id = "gemini-2.5-flash"
        self.histories = {}

    def get_session_history(self, session_id: str):
        if session_id not in self.histories:
            self.histories[session_id] = []
        return self.histories[session_id]

    def gerar_resposta_socratica(self, session_id, enunciado, entrada_aluno):
        historico = self.get_session_history(session_id)

        # Se o histórico estiver vazio, adicionamos as instruções como a primeira mensagem 'user'
        # Isso garante que o modelo siga as regras sem usar o campo problemático do JSON
        if not historico:
            instrucoes_iniciais = f"""
            Você é um tutor de matemática de IA baseado na Teoria das Situações Didáticas (Brousseau).
            Sua tarefa é mediar o aprendizado do problema: "{enunciado}"

            DIRETRIZES TÉCNICAS (Uso Interno):
            1. ANALISE o erro do aluno silenciosamente usando a Taxonomia de Radatz.
            2. FASE DE DEVOLUÇÃO: Faça o aluno assumir a responsabilidade sem dar a resposta.
            3. FASE DE VALIDAÇÃO: Se o aluno errar, apresente um contra-exemplo.
            4. INSTITUCIONALIZAÇÃO: Se o aluno acertar, formalize o conceito e encerre.

            REGRAS DE OURO:
            - NUNCA dê a resposta final.
            - Use LaTeX para toda notação matemática.
            - Seja encorajador, mas desafiador (Socrático).
            """
            historico.append({"role": "user", "parts": [{"text": instrucoes_iniciais}]})
            historico.append({"role": "model", "parts": [{"text": "Entendido. Estou pronto para mediar este problema seguindo as fases de Brousseau e a taxonomia de Radatz. Como o aluno começou?"}]})

        conteudo_atual = {"role": "user", "parts": [{"text": f"Entrada do aluno: {entrada_aluno}"}]}

        try:
            # Chamada simplificada: removemos o system_instruction do config para evitar o erro 400
            response = self.client.models.generate_content_stream(
                model=self.model_id,
                contents=historico + [conteudo_atual],
                config=types.GenerateContentConfig(
                    temperature=0.2,
                )
            )

            texto_completo = ""
            for chunk in response:
                if chunk.text:
                    texto_completo += chunk.text
                    yield chunk.text

            if texto_completo:
                historico.append(conteudo_atual)
                historico.append({"role": "model", "parts": [{"text": texto_completo}]})

        except Exception as e:
            print(f"Erro detalhado na engine: {str(e)}")
            yield f"Erro na conexão: {str(e)}"