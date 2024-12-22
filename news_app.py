from GoogleNews import GoogleNews
from datetime import datetime, timedelta
import re

def converter_data_relativa(data_str):
    hoje = datetime.now()
    
    if not data_str:
        return None
        
    if 'horas' in data_str or 'hora' in data_str:
        horas = re.findall(r'\d+', data_str)
        if horas:
            return hoje - timedelta(hours=int(horas[0]))
    elif 'dias' in data_str or 'dia' in data_str:
        dias = re.findall(r'\d+', data_str)
        if dias:
            return hoje - timedelta(days=int(dias[0]))
    elif 'semana' in data_str or 'semanas' in data_str:
        semanas = re.findall(r'\d+', data_str)
        if semanas:
            return hoje - timedelta(weeks=int(semanas[0]))
    
    return None

class NoticiasBuscador:
    def __init__(self, idioma='pt-BR', regiao='BR'):
        self.googlenews = GoogleNews(lang=idioma, region=regiao)
        
    def buscar_noticias(self, termo_busca, dias_atras=7, quantidade_paginas=2):
        """
        Busca notícias com os filtros especificados
        
        Args:
            termo_busca (str): Termo para pesquisar
            dias_atras (int): Quantidade de dias para buscar no passado
            quantidade_paginas (int): Número de páginas de resultados
            
        Returns:
            list: Lista de notícias encontradas
        """
        # Limpa resultados anteriores
        self.googlenews.clear()
        
        # Configura o período de busca
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=dias_atras)
        
        # Formata as datas no padrão mm/dd/yyyy
        data_inicio_str = data_inicio.strftime('%m/%d/%Y')
        data_fim_str = data_fim.strftime('%m/%d/%Y')
        
        # Configura o período de busca
        self.googlenews.set_time_range(data_inicio_str, data_fim_str)
        
        # Realiza a busca
        self.googlenews.search(termo_busca)
        
        # Coleta resultados de páginas adicionais
        for i in range(2, quantidade_paginas + 1):
            self.googlenews.get_page(i)
            
        # Retorna os resultados ordenados por data
        return self.googlenews.results(sort=True)

def formatar_noticia(noticia):
    """Formata uma notícia para exibição"""
    return f"""
Título: {noticia['title']}
Fonte: {noticia['media']}
Data: {noticia['date']}
Descrição: {noticia['desc']}
Link: {noticia['link']}
{'='*50}
"""

# Exemplo de uso
if __name__ == "__main__":
    # Cria o buscador
    buscador = NoticiasBuscador()
    
    # Solicita o termo de busca
    termo = input("Digite o termo para buscar notícias: ")
    
    # Prompts para o usuário
    while True:
        try:
            dias_atras = int(input("Digite quantos dias atrás você quer buscar (1-30): "))
            if 1 <= dias_atras <= 30:
                break
            else:
                print("Por favor, digite um número entre 1 e 30.")
        except ValueError:
            print("Por favor, digite um número válido.")
    
    # Realiza a busca
    try:
        noticias = buscador.buscar_noticias(
            termo_busca=termo,
            dias_atras=dias_atras,
            quantidade_paginas=2
        )
        
        # Filtro de notícias
        noticias_filtradas = []
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=dias_atras)

        for noticia in noticias:
            data_str = noticia.get('date')
            if data_str:
                data_noticia = converter_data_relativa(data_str)
                if data_noticia and data_inicio <= data_noticia <= data_fim:
                    noticias_filtradas.append(noticia)

        # Exibição dos resultados
        if noticias_filtradas:
            print(f"\nEncontradas {len(noticias_filtradas)} notícias dos últimos {dias_atras} dias:\n")
            for i, noticia in enumerate(noticias_filtradas, 1):
                print(f"Notícia {i}:")
                print(f"Título: {noticia.get('title')}")
                print(f"Data: {noticia.get('date')}")
                print(f"Fonte: {noticia.get('media')}")
                print(f"Link: {noticia.get('link')}")
                if noticia.get('desc'):
                    print(f"Descrição: {noticia.get('desc')}")
                print("=" * 50 + "\n")
        else:
            print(f"\nNenhuma notícia encontrada nos últimos {dias_atras} dias para o termo buscado.")
            
    except Exception as e:
        print(f"Erro ao buscar notícias: {str(e)}") 