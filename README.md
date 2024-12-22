# API de Notícias

API RESTful para busca de notícias usando Google News, desenvolvida com FastAPI.

## Características

- Busca notícias em português do Brasil
- Filtros por termo, data e fonte
- Paginação de resultados
- Documentação automática (Swagger/OpenAPI)

## Instalação Local

1. Clone o repositório
```bash
git clone <seu-repositorio>
cd <seu-repositorio>
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
uvicorn api_news:app --reload
```

## Endpoints

### GET /
- Verifica status da API
- Retorna: Status de funcionamento

### GET /buscar-noticias/
Busca notícias com base nos parâmetros fornecidos.

Parâmetros:
- termo (string, obrigatório): Termo de busca
- dias (int, opcional, default=7): Período de busca em dias
- fonte (string, opcional): Filtrar por fonte específica
- paginas (int, opcional, default=2): Número de páginas de resultados

## Documentação

Após iniciar a API, acesse:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deploy
Esta API está configurada para deploy automático no Railway.

## Limitações

- O Google pode limitar requisições muito frequentes
- Datas retornadas podem não ser 100% precisas
- Algumas fontes podem não estar disponíveis