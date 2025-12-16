from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import sqlite3

app = FastAPI(title="API Atos Receita Federal")

DB_NAME = "atos_api.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def criar_tabelas():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS atos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_ato TEXT,
        numero_ato TEXT,
        orgao_unidade TEXT,
        publicacao TEXT,
        ementa TEXT,
        data_consulta TEXT,
        ativo INTEGER DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs_rpa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_execucao TEXT,
        total_registros INTEGER,
        erros TEXT,
        tempo_execucao TEXT
    )
    """)

    conn.commit()
    conn.close()

criar_tabelas()

class Ato(BaseModel):
    tipo_ato: str
    numero_ato: str
    orgao_unidade: str
    publicacao: str
    ementa: str
    data_consulta: str

class LogRPA(BaseModel):
    data_execucao: str
    total_registros: int
    erros: Optional[str] = ""
    tempo_execucao: str

@app.post("/atos")
def criar_ato(ato: Ato):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO atos (
            tipo_ato, numero_ato, orgao_unidade,
            publicacao, ementa, data_consulta
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (
        ato.tipo_ato,
        ato.numero_ato,
        ato.orgao_unidade,
        ato.publicacao,
        ato.ementa,
        ato.data_consulta
    ))

    conn.commit()
    conn.close()

    return {"status": "ok"}

@app.get("/atos")
def listar_atos(
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    conn = get_conn()
    cursor = conn.cursor()

    query = "SELECT * FROM atos WHERE ativo = 1"
    params = []

    if data_inicio:
        query += " AND publicacao >= ?"
        params.append(data_inicio)

    if data_fim:
        query += " AND publicacao <= ?"
        params.append(data_fim)

    if search:
        query += " AND (tipo_ato LIKE ? OR orgao_unidade LIKE ? OR ementa LIKE ?)"
        params.extend([f"%{search}%"] * 3)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return rows

@app.put("/atos/{ato_id}")
def atualizar_ato(ato_id: int, ato: Ato):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE atos SET
            tipo_ato = ?, numero_ato = ?, orgao_unidade = ?,
            publicacao = ?, ementa = ?, data_consulta = ?
        WHERE id = ? AND ativo = 1
    """, (
        ato.tipo_ato,
        ato.numero_ato,
        ato.orgao_unidade,
        ato.publicacao,
        ato.ementa,
        ato.data_consulta,
        ato_id
    ))

    conn.commit()
    conn.close()
    return {"status": "atualizado"}

@app.delete("/atos/{ato_id}")
def deletar_ato(ato_id: int):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE atos SET ativo = 0 WHERE id = ?
    """, (ato_id,))

    conn.commit()
    conn.close()
    return {"status": "removido"}

@app.post("/logs")
def registrar_log(log: LogRPA):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO logs_rpa (
            data_execucao, total_registros, erros, tempo_execucao
        ) VALUES (?, ?, ?, ?)
    """, (
        log.data_execucao,
        log.total_registros,
        log.erros,
        log.tempo_execucao
    ))

    conn.commit()
    conn.close()
    return {"status": "log registrado"}

@app.get("/dashboard")
def dashboard():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM atos WHERE ativo = 1")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT orgao_unidade, COUNT(*) 
        FROM atos WHERE ativo = 1
        GROUP BY orgao_unidade
    """)
    por_orgao = cursor.fetchall()

    cursor.execute("""
        SELECT tipo_ato, COUNT(*) 
        FROM atos WHERE ativo = 1
        GROUP BY tipo_ato
    """)
    por_tipo = cursor.fetchall()

    conn.close()

    return {
        "total_atos": total,
        "atos_por_orgao": por_orgao,
        "atos_por_tipo": por_tipo
    }
