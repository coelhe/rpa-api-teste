
---

## 🤖 WEBSCRAPPING

Parâmetros configuráveis no código:

```python
DATA_BASE = "16/12/2025"
MODO_DATA = True  # True = 3 meses | False = 3 dias | None = data atual

📦 Instalação

1- Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

2- Instalar dependências
pip install -r requirements.txt

▶️ Executando a API Primeiro

uvicorn api:app --reload

- A API estará disponível em: http://127.0.0.1:8000
- Documentação Swagger: http://127.0.0.1:8000/docs

▶️ Executando o WebScrapping Segundamente em Terminal separado

python wc_receitas.py


