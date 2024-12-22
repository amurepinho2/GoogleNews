from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
from GoogleNews import GoogleNews
import os

app = FastAPI(title="API de Notícias",
             description="API para busca de notícias usando GoogleNews",
             version="1.0.0")

# Rota raiz para verificar se a API está funcionando
@app.get("/")
async def root():
    return {"status": "online", "message": "API de Notícias está funcionando!"}

class Noticia(BaseModel):
    titulo: str
    data: str
    fonte: str
    descricao: Optional[str]
    link: str
    id: str
    termo_busca: str

@app.get("/buscar-noticias/")
async def buscar_noticias(
    termo: str,
    dias: Optional[int] = 7,
    fonte: Optional[str] = None,
    paginas: Optional[int] = 2
):
    try:
        googlenews = GoogleNews(lang='pt', region='BR')
        
        # Configura o período de busca
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=dias)
        data_inicio_str = data_inicio.strftime('%m/%d/%Y')
        data_fim_str = data_fim.strftime('%m/%d/%Y')
        
        googlenews.set_time_range(data_inicio_str, data_fim_str)
        googlenews.search(termo)
        
        # Busca em múltiplas páginas
        for i in range(2, paginas + 1):
            googlenews.get_page(i)
            
        noticias = googlenews.result()
        noticias_filtradas = []
        
        for idx, noticia in enumerate(noticias):
            if fonte and fonte.lower() not in noticia.get('media', '').lower():
                continue
                
            noticias_filtradas.append({
                "id": f"{termo}-{idx}",
                "titulo": noticia.get('title'),
                "data": noticia.get('date'),
                "fonte": noticia.get('media'),
                "descricao": noticia.get('desc'),
                "link": noticia.get('link'),
                "termo_busca": termo
            })
        
        return noticias_filtradas
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 