import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


# Função para ler o arquivo CSV
def ler_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        print(f'Arquivo CSV lido com sucesso! Número de linhas: {len(df)}')
        return df
    except Exception as e:
        print(f'Erro ao ler o arquivo CSV: {e}')
        return None


# Função para criar o grafo de autores
def criar_grafo(df):
    G = nx.Graph()
    for _, row in df.iterrows():
        autor_principal = row['AutorPrincipal']
        coautores = row['Coautores']

        # Verifica se coautores não é NaN
        if pd.notna(coautores):
            coautores = coautores.split(';')

            # Adiciona nós e arestas
            for coautor in coautores:
                coautor = coautor.strip()
                if coautor:
                    G.add_edge(autor_principal, coautor)

    return G


# Função para calcular métricas de influência
def calcular_influencia(G, df):
    publicacoes = df['AutorPrincipal'].value_counts().to_dict()

    # Adiciona o número de publicações como atributo do nó
    nx.set_node_attributes(G, publicacoes, 'publicacoes')

    # Infla os nós com base no número de publicações
    sizes = [publicacoes.get(node, 1) * 100 for node in G.nodes()]

    return sizes


# Função para desenhar o grafo
def desenhar_grafo(G, sizes):
    pos = nx.spring_layout(G)
    plt.figure(figsize=(15, 15))
    nx.draw(G, pos, with_labels=True, node_size=sizes, node_color='skyblue', font_size=10, font_weight='bold',
            edge_color='gray')
    plt.title('Grafo de Coautoria')
    plt.show()


# Caminho do arquivo CSV
file_path = 'teste-03-publicacoesPorMembro_processed.csv'


# Execução das funções
df = ler_csv(file_path)
if df is not None:
    G = criar_grafo(df)
    sizes = calcular_influencia(G, df)
    desenhar_grafo(G, sizes)
