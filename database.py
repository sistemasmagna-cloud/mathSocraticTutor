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
        # Tabela de Interações atualizada
        conn.execute('''
            CREATE TABLE IF NOT EXISTS interacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                questao_id INTEGER, 
                sessao_id TEXT,
                entrada_aluno TEXT,
                status TEXT,
                tipo_erro TEXT,
                conceito TEXT,
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

def salvar_interacao(sessao_id, questao_id, entrada, diag, resposta):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            INSERT INTO interacoes 
            (timestamp, sessao_id, questao_id, entrada_aluno, status, tipo_erro, conceito, resposta_tutor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            sessao_id,
            questao_id,
            entrada,
            diag.get("status"),
            diag.get("tipo_erro"),
            diag.get("conceito"),
            resposta
        ))
        conn.commit()