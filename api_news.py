from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
from GoogleNews import GoogleNews
import os
from urllib.parse import urlparse, parse_qs, urlunparse
import requests
from bs4 import BeautifulSoup
import re

URLS_PERMITIDAS = [
    'braziljournal.com',
    'startups.com.br',
    'revistapegn.globo.com',
    'neofeed.com.br',
    'exame.com',
    'startupi.com.br',
    'infomoney.com.br',
    'pipelinevalor.globo.com',
    'valor.globo.com',
    'baguete.com.br',
    'finsidersbrasil.com.br',
    'bloomberglinea.com.br',
    'epocanegocios.globo.com'
]

def url_permitida(url: str) -> bool:
    """Verifica se a URL pertence às fontes permitidas"""
    if not url:
        return False
    return any(dominio in url.lower() for dominio in URLS_PERMITIDAS)

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

def extrair_imagem_da_pagina(url: str) -> Optional[str]:
    """Extrai a primeira imagem relevante da página da notícia"""
    try:
        # Faz request com headers para evitar bloqueios
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Procura por meta tags de imagem primeiro
        meta_img = soup.find('meta', property=['og:image', 'twitter:image'])
        if meta_img and meta_img.get('content'):
            return meta_img['content']
            
        # Procura por imagens no artigo
        for img in soup.find_all('img'):
            src = img.get('src', '')
            # Ignora ícones e imagens pequenas
            if src and not any(x in src.lower() for x in ['icon', 'logo', 'avatar']):
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(url))
                    src = base_url + src
                return src
                
        return None
    except Exception:
        return None

def buscar_com_termos_multiplos(googlenews: GoogleNews, termos: str) -> List[dict]:
    """
    Busca notícias com múltiplos termos usando OR
    """
    # Separa os termos pelo operador OR
    termos_lista = [termo.strip() for termo in termos.split('OR')]
    
    todas_noticias = []
    urls_vistas = set()  # Para evitar duplicatas
    
    # Busca para cada termo
    for termo in termos_lista:
        googlenews.search(termo)
        noticias = googlenews.result()
        
        # Adiciona apenas notícias não vistas
        for noticia in noticias:
            url = limpar_url(noticia.get('link', ''))  # Limpa a URL antes de comparar
            if url and url not in urls_vistas:
                urls_vistas.add(url)
                todas_noticias.append(noticia)
        
        # Limpa resultados para próxima busca
        googlenews.clear()
    
    return todas_noticias

def converter_data_relativa(data_str: str) -> datetime:
    """Converte data relativa para datetime"""
    hoje = datetime.now()
    
    if not data_str:
        return hoje
    
    try:
        if 'minuto' in data_str or 'minutos' in data_str:
            minutos = int(re.findall(r'\d+', data_str)[0])
            return hoje - timedelta(minutes=minutos)
        elif 'hora' in data_str or 'horas' in data_str:
            horas = int(re.findall(r'\d+', data_str)[0])
            return hoje - timedelta(hours=horas)
        elif 'dia' in data_str or 'dias' in data_str:
            dias = int(re.findall(r'\d+', data_str)[0])
            return hoje - timedelta(days=dias)
        elif 'semana' in data_str or 'semanas' in data_str:
            semanas = int(re.findall(r'\d+', data_str)[0])
            return hoje - timedelta(weeks=semanas)
        elif 'mês' in data_str or 'meses' in data_str:
            meses = int(re.findall(r'\d+', data_str)[0])
            return hoje - timedelta(days=meses * 30)
    except:
        pass
    
    return hoje

def ordenar_noticias_por_data(noticias: List[dict]) -> List[dict]:
    """Ordena notícias da mais recente para a mais antiga"""
    return sorted(
        noticias,
        key=lambda x: converter_data_relativa(x.get('data', '')),
        reverse=True  # True para ordem decrescente (mais recente primeiro)
    )

@app.get("/buscar-noticias/", response_model=List[dict], tags=["Notícias"])
async def buscar_noticias(
    termo: str,
    dias: Optional[int] = 7,
    fonte: Optional[str] = None,
    paginas: Optional[int] = 2,
    buscar_imagens: Optional[bool] = False
):
    """
    Busca notícias no Google News com base nos parâmetros fornecidos
    
    Args:
        termo: Termos de busca separados por OR (ex: "startup capta OR recebe aporte")
        dias: Período de busca em dias (padrão: 7)
        fonte: Filtrar por fonte específica (opcional)
        paginas: Número de páginas de resultados (padrão: 2)
        buscar_imagens: Se deve tentar extrair imagens das páginas (padrão: False)
    """
    try:
        # Inicializa o GoogleNews com configurações para PT-BR
        googlenews = GoogleNews(lang='pt', region='BR')
        
        # Configura o período de busca
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=dias)
        data_inicio_str = data_inicio.strftime('%m/%d/%Y')
        data_fim_str = data_fim.strftime('%m/%d/%Y')
        googlenews.set_time_range(data_inicio_str, data_fim_str)
        
        # Busca com múltiplos termos
        noticias = buscar_com_termos_multiplos(googlenews, termo)
        noticias_unicas = {}
        
        # Processa e filtra os resultados
        for idx, noticia in enumerate(noticias):
            if fonte and fonte.lower() not in noticia.get('media', '').lower():
                continue
                
            url = limpar_url(noticia.get('link'))
            
            # Adiciona verificação de URL permitida
            if not url or url in noticias_unicas or not url_permitida(url):
                continue
                
            imagem_url = None
            if buscar_imagens and url:
                imagem_url = extrair_imagem_da_pagina(url)
                
            noticias_unicas[url] = {
                "id": f"{termo.replace(' OR ', '-')}-{idx}",
                "titulo": noticia.get('title'),
                "data": noticia.get('date'),
                "fonte": noticia.get('media'),
                "descricao": noticia.get('desc'),
                "link": url,
                "imagem": imagem_url,
                "termo_busca": termo
            }
        
        # Converte o dicionário em lista e ordena
        noticias_filtradas = list(noticias_unicas.values())
        noticias_filtradas = ordenar_noticias_por_data(noticias_filtradas)
        
        return noticias_filtradas
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar notícias: {str(e)}"
        ) 