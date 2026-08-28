import sqlite3
from datetime import datetime

DB_NAME = "pesquisa_doutorado.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        # Tabela de Questões
        conn.execute('''
            CREATE TABLE IF NOT EXISTS questoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                enunciado TEXT NOT NULL,
                url_imagem TEXT,
                link_externo TEXT
            )
        ''')
        # Tabela de Interações atualizada com a Análise Dual (Radatz + Brousseau)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS interacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                questao_id INTEGER, 
                sessao_id TEXT,
                entrada_aluno TEXT,
                status_resposta TEXT,
                categoria_radatz TEXT,
                termo_didatico TEXT,
                evidencia_erro TEXT,
                sugestao_intervencao TEXT,
                resposta_tutor TEXT,
                FOREIGN KEY (questao_id) REFERENCES questoes (id)
            )
        ''')
        conn.commit()

def cadastrar_questao(enunciado, url_imagem=None, link_externo=None):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO questoes (timestamp, enunciado, url_imagem, link_externo)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), enunciado, url_imagem, link_externo))
        conn.commit()
        return cursor.lastrowid

def obter_questao(questao_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM questoes WHERE id = ?', (questao_id,))
        return cursor.fetchone()

def salvar_interacao(sessao_id, questao_id, entrada, diag, resposta, status_resposta="incorreta"):
    """
    Salva a interação recebendo o dicionário 'diag' gerado para o professor.
    """
    # Garante que 'diag' seja um dicionário mesmo se vier nulo por segurança
    diag = diag if isinstance(diag, dict) else {}

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            INSERT INTO interacoes 
            (timestamp, sessao_id, questao_id, entrada_aluno, status_resposta, 
             categoria_radatz, termo_didatico, evidencia_erro, sugestao_intervencao, resposta_tutor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            sessao_id,
            questao_id,
            entrada,
            status_resposta,
            diag.get("categoria_radatz", "Não classificado"),
            diag.get("termo_didatico", "Não classificado"),
            diag.get("evidencia_erro", ""),
            diag.get("sugestao_intervencao", ""),
            resposta
        ))
        conn.commit()