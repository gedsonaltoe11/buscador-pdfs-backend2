from fastapi import FastAPI, Query
import httpx
import os

app = FastAPI()

UNPAYWALL_EMAIL = os.getenv("UNPAYWALL_EMAIL", "Gedson.altoe11@gmail.com")

async def buscar_openalex(query: str):
    url = f"https://api.openalex.org/works?search={query}&per-page=5"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code == 200:
            data = r.json().get("results", [])
            resultados = []
            for item in data:
                resultados.append({
                    "titulo": item.get("title"),
                    "ano": item.get("publication_year"),
                    "pdf": item.get("open_access", {}).get("oa_url"),
                    "fonte": "OpenAlex"
                })
            return resultados
    return []

async def buscar_crossref(query: str):
    url = f"https://api.crossref.org/works?query={query}&rows=5"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code == 200:
            items = r.json().get("message", {}).get("items", [])
            resultados = []
            for item in items:
                doi = item.get("DOI")
                pdf_url = None
                if doi:
                    uurl = f"https://api.unpaywall.org/v2/{doi}?email={UNPAYWALL_EMAIL}"
                    ur = await client.get(uurl)
                    if ur.status_code == 200:
                        pdf_url = ur.json().get("best_oa_location", {}).get("url_for_pdf")
                resultados.append({
                    "titulo": item.get("title", ["Sem título"])[0],
                    "ano": item.get("issued", {}).get("date-parts", [[None]])[0][0],
                    "pdf": pdf_url,
                    "fonte": "Crossref"
                })
            return resultados
    return []

@app.get("/buscar")
async def buscar(query: str = Query(..., description="Termo de busca")):
    openalex = await buscar_openalex(query)
    crossref = await buscar_crossref(query)
    return {"resultados": openalex + crossref}
