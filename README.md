
## 🤖 WEBSCRAPPING





## Parâmetros configuráveis no código:


`DATA_BASE = "16/12/2025"`

`MODO_DATA = True` ### True=3meses | False=3dias | None=data atual


## 📦 Instalação

Clonar o projeto
```bash
git clone https://github.com/coelhe/rpa-api-teste.git
```

Entre na pasta
```bash
cd rpa-api-teste
```

Criar/Ativar ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

Instalar dependências
```bash
pip install -r requirements.txt
```


## ▶️ Executando o WebScrapping/API

Primeiro abrir a API
```bash
uvicorn api:app --reload
```
- A API estará disponível em: http://127.0.0.1:8000
- Documentação Swagger: http://127.0.0.1:8000/docs

Segundo executar o robô em outro terminal
```bash
python wc_receitas.py
```
