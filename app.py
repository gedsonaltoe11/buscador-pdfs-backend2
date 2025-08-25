from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI()

# Permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Email obrigatório para Unpaywall
UNPAYWALL_EMAIL = os.getenv("UNPAYWALL_EMAIL", "Gedson.altoe11@gmail.com")


@app.get("/buscar")
async def buscar(query: str):
    resultados = []

    async with httpx.AsyncClient() as client:
        # ========== OpenAlex ==========
        try:
            resp = await client.get(
                "https://api.openalex.org/works",
                params={"search": query, "per_page": 5},
                timeout=10
            )
            data = {}
            try:
                data = resp.json()
            except Exception:
                data = {}
            for r in data.get("results", []):
                resultados.append({
                    "titulo": r.get("title"),
                    "autores": [a.get("author", {}).get("display_name") for a in r.get("authorships", [])],
                    "ano": r.get("publication_year"),
                    "link": r.get("doi"),
                    "fonte": "OpenAlex"
                })
        except Exception as e:
            print("Erro OpenAlex:", e)

        # ========== Crossref ==========
        try:
            resp = await client.get(
                "https://api.crossref.org/works",
                params={"query": query, "rows": 5},
                timeout=10
            )
            data = {}
            try:
                data = resp.json()
            except Exception:
                data = {}
            for r in data.get("message", {}).get("items", []):
                resultados.append({
                    "titulo": r.get("title", ["Sem título"])[0],
                    "autores": [a.get("family") for a in r.get("author", []) if "family" in a],
                    "ano": r.get("issued", {}).get("date-parts", [[None]])[0][0],
                    "link": r.get("URL"),
                    "fonte": "Crossref"
                })
        except Exception as e:
            print("Erro Crossref:", e)

        # ========== Unpaywall ==========
        try:
            resp = await client.get(
                "https://api.unpaywall.org/v2/search",
                params={"query": query, "email": UNPAYWALL_EMAIL},
                timeout=10
            )
            data = {}
            try:
                data = resp.json()
            except Exception:
                data = {}
            for r in data.get("results", []):
                resultados.append({
                    "titulo": r.get("title"),
                    "autores": r.get("z_authors"),
                    "ano": r.get("year"),
                    "link": r.get("best_oa_location", {}).get("url_for_pdf"),
                    "fonte": "Unpaywall"
                })
        except Exception as e:
            print("Erro Unpaywall:", e)

    return {"resultados": resultados}
