from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
from GoogleNews import GoogleNews
import os
from urllib.parse import urlparse, parse_qs, urlunparse

# Configuração da API FastAPI com metadados
app = FastAPI(
    title="API de Notícias",
    description="API para busca de notícias do Google News com filtros personalizados",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Modelo de dados para as notícias
class Noticia(BaseModel):
    titulo: str
    data: str
    fonte: str
    descricao: Optional[str]
    link: str
    id: str
    termo_busca: str

# Rota de verificação de saúde da API
@app.get("/", tags=["Status"])
async def root():
    """Verifica se a API está funcionando"""
    return {
        "status": "online",
        "message": "API de Notícias está funcionando!",
        "docs": "/docs"
    }

def limpar_url(url: str) -> str:
    """Remove parâmetros de rastreamento do Google da URL"""
    if not url:
        return url
        
    try:
        # Parse a URL
        parsed = urlparse(url)
        # Remove parâmetros de rastreamento
        query = parse_qs(parsed.query)
        query = {k: v for k, v in query.items() if not k in ['ved', 'usg']}
        # Reconstrói a URL limpa
        clean_url = parsed._replace(query='&'.join(f'{k}={v[0]}' for k, v in query.items()))
        return urlunparse(clean_url).split('&ved=')[0].split('&usg=')[0]
    except:
        return url

@app.get("/buscar-noticias/", response_model=List[dict], tags=["Notícias"])
async def buscar_noticias(
    termo: str,
    dias: Optional[int] = 7,
    fonte: Optional[str] = None,
    paginas: Optional[int] = 2
):
    """
    Busca notícias no Google News com base nos parâmetros fornecidos
    
    Args:
        termo: Palavra-chave para busca
        dias: Período de busca em dias (padrão: 7)
        fonte: Filtrar por fonte específica (opcional)
        paginas: Número de páginas de resultados (padrão: 2)
    
    Returns:
        Lista de notícias encontradas
    """
    try:
        # Inicializa o GoogleNews com configurações para PT-BR
        googlenews = GoogleNews(lang='pt', region='BR')
        
        # Configura o período de busca
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=dias)
        data_inicio_str = data_inicio.strftime('%m/%d/%Y')
        data_fim_str = data_fim.strftime('%m/%d/%Y')
        
        # Configura e executa a busca
        googlenews.set_time_range(data_inicio_str, data_fim_str)
        googlenews.search(termo)
        
        # Busca páginas adicionais se solicitado
        for i in range(2, paginas + 1):
            googlenews.get_page(i)
            
        noticias = googlenews.result()
        noticias_filtradas = []
        
        # Processa e filtra os resultados
        for idx, noticia in enumerate(noticias):
            # Aplica filtro de fonte se especificado
            if fonte and fonte.lower() not in noticia.get('media', '').lower():
                continue
                
            noticias_filtradas.append({
                "id": f"{termo}-{idx}",
                "titulo": noticia.get('title'),
                "data": noticia.get('date'),
                "fonte": noticia.get('media'),
                "descricao": noticia.get('desc'),
                "link": limpar_url(noticia.get('link')),
                "termo_busca": termo
            })
        
        return noticias_filtradas
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar notícias: {str(e)}"
        ) 