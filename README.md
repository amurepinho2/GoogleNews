# API de Notícias

API para busca de notícias usando GoogleNews, desenvolvida com FastAPI.

## Instalação Local

1. Clone o repositório
2. Instale as dependências:
```
pip install GoogleNews
```

## Uso
- Inicialização
```
from GoogleNews import GoogleNews
googlenews = GoogleNews()
```
- Verificar versão
```
print(googlenews.getVersion())
```
- Habilitar exceções
```
googlenews.enableException(True)
```
- Escolher idioma
```
googlenews = GoogleNews(lang='en')
```
ou
```
googlenews = GoogleNews(lang='en', region='US')
```
- Escolher período
```
googlenews = GoogleNews(period='7d')
```
- Escolher intervalo de datas
```
googlenews = GoogleNews(start='02/01/2020',end='02/28/2020')
```
- Definir codificação
```
googlenews = GoogleNews(encode='utf-8')
```
ou
```
googlenews.set_lang('en')
googlenews.set_period('7d')
googlenews.set_time_range('02/01/2020','02/28/2020')
googlenews.set_encode('utf-8')
```
- **news.google.com** busca de exemplo
```
googlenews.get_news('APPLE')
```
- **news.google.com busca notícias por tópicos
```
# Esportes
googlenews.set_topic('CAAqKggKIiRDQkFTRlFvSUwyMHZNRFp1ZEdvU0JYQjBMVUpTR2dKQ1VpZ0FQAQ')
googlenews.get_news()
```
- **news.google.com busca notícias por tópico e seções
```
# Esportes
googlenews.set_topic('CAAqKggKIiRDQkFTRlFvSUwyMHZNRFp1ZEdvU0JYQjBMVUpTR2dKQ1VpZ0FQAQ')
# Futebol
googlenews.set_section('CAQiS0NCQVNNZ29JTDIwdk1EWnVkR29TQlhCMExVSlNHZ0pDVWlJT0NBUWFDZ29JTDIwdk1ESjJlRFFxQ3dvSkVnZEdkWFJsWW05c0tBQSouCAAqKggKIiRDQkFTRlFvSUwyMHZNRFp1ZEdvU0JYQjBMVUpTR2dKQ1VpZ0FQAVAB')

googlenews.get_news()
```
- **google.com** busca de notícias de seção
```
googlenews.search('APPLE')
```

Por padrão, retorna o primeiro resultado da página, você não precisa buscar a primeira página novamente, caso contrário, você pode obter resultados duplicados. Para obter outra página de resultados de busca:

```
googlenews.get_page(2)
```
- Se você quiser obter uma página específica
```
result = googlenews.page_at(2)
```
- Se você quiser obter o número total de resultados da busca (este é um número aproximado, não exato, é o número mostrado na página de busca do Google) (Nota: esta função não está disponível para `googlenews.search()`)
```
googlenews.total_count()
```
- Obter resultados retorna a lista, `[{'title': '...', 'media': '...', 'date': '...', 'datetime': '...', 'desc': '...', 'link': '...', 'img': '...'}]`
```
googlenews.results()
```
Se `googlenews.results(sort=True)` o utilitário tentará ordenar os resultados em ordem cronológica reversa

- Obter textos retorna a lista de títulos de notícias
```
googlenews.get_texts()
```
- Obter links retorna a lista de links de notícias
```
googlenews.get_links()
```
- Limpar lista de resultados antes de fazer outra busca com o mesmo objeto
```
googlenews.clear()
```
## Problemas
A imagem não está funcionando na versão mais recente, ela só pode retornar o gif de carregamento do google padrão

O intervalo de datas não sempre funciona como o Google pode retornar resultados com ordem aleatória ou fora do intervalo de datas.

O Google pode reconhecer o programa como robôs automatizados e bloquear o IP, usando servidor em nuvem e buscando dados com alta frequência terá mais chance de ser bloqueado. 


bash
pip install -r requirements.txt

3. Execute a aplicação:
bash
uvicorn api_news:app --reload


## Endpoints

### GET /buscar-noticias/
Busca notícias com base nos parâmetros fornecidos.

Parâmetros:
- termo (string, obrigatório): Termo de busca
- dias (int, opcional, default=7): Período de busca em dias
- fonte (string, opcional): Filtrar por fonte específica
- paginas (int, opcional, default=2): Número de páginas de resultados

## Deploy
Esta API está configurada para deploy automático no Railway.