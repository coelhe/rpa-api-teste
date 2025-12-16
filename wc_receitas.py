from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import sqlite3
import time
import requests

URL = "http://normas.receita.fazenda.gov.br/sijut2consulta/consulta.action"
DB_NAME = "atos_receita.db"
API_URL = "http://127.0.0.1:8000/atos"
DATA_BASE = "16/12/2025"
MODO_DATA = True #True=3MesesAntes - False=3DiasAntes - None=Vazio

inicio_execucao = datetime.now()

def inicializar_banco():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS atos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_ato TEXT,
        numero_ato TEXT,
        orgao_unidade TEXT,
        publicacao TEXT,
        ementa TEXT,
        data_consulta TEXT
    )
    """)

    conn.commit()
    return conn, cursor

def extrair_tabela(driver, cursor, conn, data_consulta):
    tabela = driver.find_element(By.TAG_NAME, "table")
    linhas = tabela.find_elements(By.TAG_NAME, "tr")[1:]

    registros = 0

    for linha in linhas:
        colunas = linha.find_elements(By.TAG_NAME, "td")
        if len(colunas) < 5:
            continue

        registro = {
            "tipo_ato": colunas[0].text.strip(),
            "numero_ato": colunas[1].text.strip(),
            "orgao_unidade": colunas[2].text.strip(),
            "publicacao": colunas[3].text.strip(),
            "ementa": colunas[4].text.strip(),
            "data_consulta": data_consulta
        }

        #Backup Local
        cursor.execute("""
            INSERT INTO atos (
                tipo_ato,
                numero_ato,
                orgao_unidade,
                publicacao,
                ementa,
                data_consulta
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            registro["tipo_ato"],
            registro["numero_ato"],
            registro["orgao_unidade"],
            registro["publicacao"],
            registro["ementa"],
            registro["data_consulta"]
        ))

        try:
            response = requests.post(API_URL, json=registro, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Erro ao enviar registro para API: {e}")

        registros += 1

    conn.commit()
    return registros

def ir_para_proxima_pagina(driver, wait):
    try:
        botao = driver.find_element(By.ID, "btnProximaPagina2")

        if not botao.is_displayed():
            return False

        botao.click()

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        time.sleep(1)

        return True
    except:
        return False

def data_meses(data_base_str, modo):

    if data_base_str is None or modo is None:
        return None

    data_base = datetime.strptime(data_base_str, "%d/%m/%Y")

    if modo is True:
        data_inicio = data_base - relativedelta(months=3)
    else:
        data_inicio = data_base - timedelta(days=3)

    return data_inicio.strftime("%d/%m/%Y")

def main():
    conn, cursor = inicializar_banco()

    options = Options()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(), options=options)
    wait = WebDriverWait(driver, 20)

    driver.get(URL)
    wait.until(EC.presence_of_element_located((By.ID, "dt_inicio")))
    print("Formulário carregado")

    DATA_INICIO = data_meses(DATA_BASE, MODO_DATA)

    dt_inicio = driver.find_element(By.ID, "dt_inicio")
    dt_fim = driver.find_element(By.ID, "dt_fim")

    dt_inicio.clear()
    dt_inicio.send_keys(DATA_INICIO)

    dt_fim.clear()
    dt_fim.send_keys(DATA_BASE)

    driver.find_element(By.ID, "btnSubmit").click()

    wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
    time.sleep(1)

    total = 0
    pagina = 1

    while True:
        print(f"\nProcessando página {pagina}...")
        total += extrair_tabela(driver, cursor, conn, DATA_INICIO)
        print(f"Total capturado até agora: {total}")

        if not ir_para_proxima_pagina(driver, wait):
            break

        pagina += 1
    fim_execucao = datetime.now()
    tempo_execucao = str(fim_execucao - inicio_execucao)
    
    log = {
        "data_execucao": inicio_execucao.strftime("%d/%m/%Y %H:%M:%S"),
        "total_registros": total,
        "erros": "",
        "tempo_execucao": tempo_execucao
    }
    try:
        requests.post("http://127.0.0.1:8000/logs", json=log)
    except Exception as e:
        print("Erro ao enviar log para API:", e)

    driver.quit()
    conn.close()    
    print("\nRPA FINALIZADO COM SUCESSO")
    print(f"TOTAL DE REGISTROS CAPTURADOS: {total}")

if __name__ == "__main__":
    main()
