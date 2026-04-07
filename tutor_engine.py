import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


class MathTutorEngine:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            #model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.1
        )
        self.histories = {}  # Dicionário para gerenciar múltiplas sessões de alunos

    def get_session_history(self, session_id: str):
        if session_id not in self.histories:
            self.histories[session_id] = ChatMessageHistory()
        return self.histories[session_id]

    def analisar_erro(self, enunciado, entrada):
        # Implementação da Taxonomia de Radatz
        prompt = f"""
        Enunciado: {enunciado}
        Resposta do Aluno: {entrada}

        Analise o erro do aluno com base na Taxonomia de Radatz e retorne APENAS JSON:
        - Dificuldade de Linguagem (compreensão de termos)
        - Processamento Espacial (interpretação de figuras/gráficos)
        - Associações Deficientes (regra certa em contexto errado)
        - Regras Irrelevantes (aplicação de 'macetes' sem sentido)
        - Erro de Execução (falha no cálculo puramente)

        {{ 
          "status": "erro/parcial/acerto", 
          "tipo_erro": "Categoria de Radatz", 
          "conceito": "Tópico matemático", 
          "sugestao": "Pergunta para fase de Validação de Brousseau" 
        }}
        """
        res = self.llm.invoke(prompt)
        # Limpeza robusta do JSON
        content = res.content.strip().replace("```json", "").replace("```", "")
        return json.loads(content)

    def gerar_resposta(self, session_id, enunciado, entrada, diag):

        # Verificamos se o aluno já acertou segundo o diagnóstico de Radatz
        if diag.get('status') == 'acerto':
            system_instructions = f"""
            És um mediador baseado na Teoria das Situações Didáticas de Brousseau.
            O aluno ACERTOU o problema: {enunciado}.
    
            REGRAS DE FINALIZAÇÃO:
            1. Reconheça formalmente o acerto (Fase de Institucionalização).
            2. Sintetize o que foi aprendido (ex: a relação multiplicativa das áreas).
            3. Encerre a conversa de forma motivadora, sem fazer novas perguntas.
            4. Use LaTeX.
            """
        else:
            # Lógica anterior de mediação para erros ou acertos parciais
            system_instructions = f"""
            És um mediador baseado na Teoria das Situações Didáticas de Brousseau.
            Problema: {enunciado}
            Diagnóstico (Radatz): {diag['tipo_erro']}
    
            REGRAS DE INTERAÇÃO:
            1. Nunca dês a resposta.
            2. Fase de Devolução: Faz com que o aluno aceite a responsabilidade pelo problema.
            3. Fase de Validação: Se o aluno errar, não corrijas. Apresenta um contra-exemplo ou pede para ele verificar a lógica.
            4. Se for 'Dificuldade de Linguagem', pede para ele explicar o que entendeu de um termo específico.
            5. Usa LaTeX para termos matemáticos.
            """

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_instructions),
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