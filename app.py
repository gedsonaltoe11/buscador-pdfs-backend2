from fastapi import FastAPI
import requests
import os

app = FastAPI()

# Pegando o email da variável de ambiente
UNPAYWALL_EMAIL = os.getenv("UNPAYWALL_EMAIL")

@app.get("/")
def raiz():
    return {
        "status": "API funcionando 🚀",
        "como_usar": "Acesse /buscar?query=python para testar",
        "exemplo": "/buscar?query=python"
    }

@app.get("/buscar")
def buscar(query: str):
    if not UNPAYWALL_EMAIL:
        return {"erro": "Variável UNPAYWALL_EMAIL não configurada no Render"}

    url = f"https://api.unpaywall.org/v2/search?query={query}&email={UNPAYWALL_EMAIL}"
    response = requests.get(url)

    if response.status_code != 200:
        return {"erro": "Falha ao buscar no Unpaywall", "status_code": response.status_code}

    data = response.json()
    resultados = []
    for item in data.get("results", []):
        doi = item.get("doi")
        title = item.get("title")
        pdf_url = item.get("best_oa_location", {}).get("url_for_pdf")
        if pdf_url:
            resultados.append({
                "title": title,
                "doi": doi,
                "pdf_url": pdf_url
            })

    return {"q": query, "total": len(resultados), "resultados": resultados}
