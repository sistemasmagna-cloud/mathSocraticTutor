import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


class MathTutorEngine:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.1
        )
        self.histories = {}  # Dicionário para gerenciar múltiplas sessões de alunos

    def get_session_history(self, session_id: str):
        if session_id not in self.histories:
            self.histories[session_id] = ChatMessageHistory()
        return self.histories[session_id]

    def analisar_erro(self, enunciado, entrada):
        prompt = f"""
        Enunciado: {enunciado}
        Resposta do Aluno: {entrada}
        Analise pedagogicamente e retorne APENAS JSON:
        {{ "status": "erro/acerto", "tipo_erro": "conceitual/procedural/interpretacao", "conceito": "topico", "sugestao": "dica" }}
        """
        res = self.llm.invoke(prompt)
        return json.loads(res.content.strip().replace("```json", "").replace("```", ""))

    def gerar_resposta(self, session_id, enunciado, entrada, diag):
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", f"És um Tutor Socrático. Problema: {enunciado}. Erro: {diag['tipo_erro']}. Use LaTeX."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{texto}")
        ])

        chain = RunnableWithMessageHistory(
            prompt_template | self.llm,
            self.get_session_history,
            input_messages_key="texto",
            history_messages_key="history"
        )

        return chain.invoke({"texto": entrada}, config={"configurable": {"session_id": session_id}}).content