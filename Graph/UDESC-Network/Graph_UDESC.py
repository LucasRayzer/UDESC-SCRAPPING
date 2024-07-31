import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import re
import unidecode


#Função para ler o arquivo CSV de publicações
def ler_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        print(f'Arquivo CSV lido com sucesso! Número de linhas: {len(df)}')
        return df
    except Exception as e:
        print(f'Erro ao ler o arquivo CSV: {e}')
        return None


#Função para ler o arquivo TXT de citações
def ler_citacoes(file_path):
    try:
        citacoes = {}
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file):
                if line_num == 0:  # Pular a primeira linha
                    continue
                if line.strip():
                    name, variations = line.split(',', 1)
                    variations = [v.strip() for v in variations.split(';')]
                    citacoes[name.strip()] = variations
        print(f'Arquivo de citações lido com sucesso! Número de autores: {len(citacoes)}')
        return citacoes
    except Exception as e:
        print(f'Erro ao ler o arquivo de citações: {e}')
        return None


#Função para normalizar os nomes
def normalizar_nome(nome):
    nome = re.sub(r'"', '', nome)  # Remove aspas
    nome = unidecode.unidecode(nome)  #Remoção de acentos
    nome = re.sub(r'\s+', ' ', nome)  #Remoção de múltiplos espaços
    return nome.strip().lower()  #Remoção de espaços desnecessários e converte para minúsculas


# Função para criar o grafo de autores
def criar_grafo(df, citacoes):
    G = nx.Graph()  # Cria um grafo não-direcionado

    #Mapeia as variações de nome para os autores principais
    global nome_para_autor
    nome_para_autor = {}
    for principal_author, variations in citacoes.items():
        principal_author_normalizado = normalizar_nome(principal_author)
        nome_para_autor[principal_author_normalizado] = principal_author
        for var in variations:
            nome_normalizado = normalizar_nome(var)
            nome_para_autor[nome_normalizado] = principal_author

    #Adiciona nós dos autores principais ao grafo
    for principal_author in citacoes.keys():
        G.add_node(principal_author)

    #Adiciona arestas entre os autores principais e seus coautores
    for index, row in df.iterrows():
        citing_author = normalizar_nome(row['AutorPrincipal'])
        coautores = row['Coautores']

        if pd.notna(coautores) and isinstance(coautores, str):
            coautores_list = [normalizar_nome(c) for c in coautores.split(';')]

            #Verifica cada coautor e cria arestas apropriadas
            for coautor in coautores_list:
                if coautor in nome_para_autor:
                    cited_author = nome_para_autor[coautor]
                    normalized_citing_author = nome_para_autor.get(citing_author, citing_author)

                    #Ignora arcos/Auto-Citações
                    if normalized_citing_author != cited_author:
                        if G.has_edge(normalized_citing_author, cited_author):
                            G[normalized_citing_author][cited_author]['weight'] += 1
                        else:
                            G.add_edge(normalized_citing_author, cited_author, weight=1)
                        print(f'Debug: "{normalized_citing_author}" (Principal) citou "{cited_author}" (Coautor)')
                    else:
                        print(
                            f'Aviso: Ignorando auto-citação para "{normalized_citing_author}" citando "{cited_author}"')
                else:
                    print(f'Aviso: "{coautor}" não encontrado em Citacoes.txt')

    #Remove os nós que não têm arestas
    isolated_nodes = [node for node, degree in dict(G.degree()).items() if degree == 0]
    G.remove_nodes_from(isolated_nodes)
    print(f'Nodos isolados removidos: {isolated_nodes}')

    return G



#Função para calcular métricas de influência
def calcular_influencia(G, df, citacoes):
    #Conta o número de publicações para cada autor principal
    publicacoes = {autor: 0 for autor in citacoes.keys()}

    for autor in df['AutorPrincipal']:
        autor_normalizado = normalizar_nome(autor)
        if autor_normalizado in nome_para_autor:
            autor_principal = nome_para_autor[autor_normalizado]
            publicacoes[autor_principal] += 1

    #Adiciona o atributo 'publicacoes' aos nós
    nx.set_node_attributes(G, publicacoes, 'publicacoes')

    #Determina o tamanho dos nós com base no número de publicações
    sizes = [publicacoes.get(node, 1) * 10 for node in G.nodes()]

    return sizes, publicacoes


#Função para desenhar o grafo com cores baseadas no número de publicações
def desenhar_grafo(G, sizes, publicacoes):
    pos = nx.spring_layout(G, k=0.8, iterations=75)

    #Determina a cor dos nós com base no número de publicações
    max_publicacoes = max(publicacoes.values())
    min_publicacoes = min(publicacoes.values())

    cmap = plt.get_cmap('coolwarm')
    node_colors = [publicacoes[node] for node in G.nodes()]

    plt.figure(figsize=(25, 25))
    nx.draw_networkx_edges(G, pos, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')

    sc = plt.scatter([], [], c=[], cmap=cmap, vmin=min_publicacoes, vmax=max_publicacoes)
    nodes = nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color=node_colors, cmap=cmap, vmin=min_publicacoes, vmax=max_publicacoes)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=mcolors.Normalize(vmin=min_publicacoes, vmax=max_publicacoes))
    sm.set_array([])
    plt.colorbar(sc, label='Número de Publicações')
    plt.title('Grafo de Coautoria')
    plt.show()


#Função para exportar o grafo em txt
def exportar_grafo_texto(G, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('Vértices (Autores):\n')
        for node in G.nodes(data=True):
            publicacoes = node[1].get('publicacoes', 0)  #Pega o número de publicações, ou 0 em casos especiais
            file.write(f'{node[0]}: {publicacoes} publicações\n')

        file.write('\nArestas (Coautoria) e Pesos:\n')
        for edge in G.edges(data=True):
            file.write(f'{edge[0]} - {edge[1]}: {edge[2]["weight"]} coautorias\n')

    print(f'Grafo exportado para {file_path} com sucesso!')


#Caminhos dos arquivos
file_path_publicacoes = 'modified_new.csv'
file_path_citacoes = 'Citacoes.txt'
file_path_grafo_texto = 'grafo.txt'

#Execução das funções
df_publicacoes = ler_csv(file_path_publicacoes)
citacoes = ler_citacoes(file_path_citacoes)

if df_publicacoes is not None and citacoes is not None:
    G = criar_grafo(df_publicacoes, citacoes)
    sizes, publicacoes = calcular_influencia(G, df_publicacoes, citacoes)
    desenhar_grafo(G, sizes, publicacoes)
    exportar_grafo_texto(G, file_path_grafo_texto)
