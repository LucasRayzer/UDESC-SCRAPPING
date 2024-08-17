import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import re
import unidecode
import numpy as np

# Função para ler o arquivo CSV de publicações
def ler_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        print(f'Arquivo CSV lido com sucesso! Número de linhas: {len(df)}')
        return df
    except Exception as e:
        print(f'Erro ao ler o arquivo CSV: {e}')
        return None

# Função para ler o arquivo TXT de citações
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

# Função para normalizar os nomes
def normalizar_nome(nome):
    nome = re.sub(r'"', '', nome)  # Remove aspas
    nome = unidecode.unidecode(nome)  # Remoção de acentos
    nome = re.sub(r'\s+', ' ', nome)  # Remoção de múltiplos espaços
    return nome.strip().lower()  # Remoção de espaços desnecessários e converte para minúsculas

# Função para criar a abreviação dos nomes
def abreviar_nome(nome):
    nome = re.sub(r'"', '', nome)  # Remove aspas
    abreviacao = ''.join([letra for letra in nome if letra.isupper()])
    return abreviacao if abreviacao else nome[:3].upper()  # Caso não haja letras maiúsculas, usa as três primeiras letras

# Função para criar o grafo de autores
def criar_grafo(df, citacoes):
    G = nx.Graph()  # Cria um grafo não-direcionado

    # Mapeia as variações de nome para os autores principais
    global nome_para_autor, abreviacoes
    nome_para_autor = {}
    abreviacoes = {}

    for principal_author, variations in citacoes.items():
        principal_author_normalizado = normalizar_nome(principal_author)
        abreviacoes[principal_author] = abreviar_nome(principal_author)
        nome_para_autor[principal_author_normalizado] = principal_author
        for var in variations:
            nome_normalizado = normalizar_nome(var)
            nome_para_autor[nome_normalizado] = principal_author

    # Adiciona nós dos autores principais ao grafo
    for principal_author in citacoes.keys():
        G.add_node(principal_author)

    # Adiciona arestas entre os autores principais e seus coautores
    for index, row in df.iterrows():
        citing_author = normalizar_nome(row['AutorPrincipal'])
        coautores = row['Coautores']

        if pd.notna(coautores) and isinstance(coautores, str):
            coautores_list = [normalizar_nome(c) for c in coautores.split(';')]

            # Verifica cada coautor e cria arestas apropriadas
            for coautor in coautores_list:
                if coautor in nome_para_autor:
                    cited_author = nome_para_autor[coautor]
                    normalized_citing_author = nome_para_autor.get(citing_author, citing_author)

                    # Ignora arcos/Auto-Citações
                    if normalized_citing_author != cited_author:
                        if G.has_edge(normalized_citing_author, cited_author):
                            G[normalized_citing_author][cited_author]['weight'] += 1
                        else:
                            G.add_edge(normalized_citing_author, cited_author, weight=1)

    # Remove os nós que não têm arestas
    isolated_nodes = [node for node, degree in dict(G.degree()).items() if degree == 0]
    G.remove_nodes_from(isolated_nodes)
    print(f'Nodos isolados removidos: {isolated_nodes}')

    return G

# Função para calcular métricas de influência
def calcular_influencia(G, df, citacoes):
    # Conta o número de publicações para cada autor principal
    publicacoes = {autor: 0 for autor in citacoes.keys()}

    for autor in df['AutorPrincipal']:
        autor_normalizado = normalizar_nome(autor)
        if autor_normalizado in nome_para_autor:
            autor_principal = nome_para_autor[autor_normalizado]
            publicacoes[autor_principal] += 1

    # Adiciona o atributo 'publicacoes' aos nós
    nx.set_node_attributes(G, publicacoes, 'publicacoes')

    # Determina o tamanho dos nós com base no número de publicações
    sizes = [publicacoes.get(node, 1) * 8 for node in G.nodes()]

    return sizes, publicacoes

# Função para calcular métricas de centralidade
def calcular_centralidade(G):
    # Número de coautores, o maior é o que mais tem arestas conectadas com os outros nós
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    closeness_centrality = nx.closeness_centrality(G)

    nx.set_node_attributes(G, degree_centrality, 'degree_centrality')
    nx.set_node_attributes(G, betweenness_centrality, 'betweenness_centrality')
    nx.set_node_attributes(G, closeness_centrality, 'closeness_centrality')

    return degree_centrality, betweenness_centrality, closeness_centrality

# Função para calcular as métricas adicionais solicitadas
def calcular_metricas_adicionais(G):
    num_arestas = G.number_of_edges()
    numero_de_nos = G.number_of_nodes()

    # Verifica se o grafo é conexo
    if nx.is_connected(G):
        diametro = nx.diameter(G)
        caminho_medio = nx.average_shortest_path_length(G)
    else:
        # Calcula o diâmetro e caminho médio para cada componente conexo
        componentes_conexos = (G.subgraph(c).copy() for c in nx.connected_components(G))
        diametro = max(nx.diameter(subgraph) for subgraph in componentes_conexos)

        # Calcula o caminho médio para cada componente conexo
        componentes_conexos = (G.subgraph(c).copy() for c in nx.connected_components(G))
        caminho_medio = np.mean([nx.average_shortest_path_length(subgraph) for subgraph in componentes_conexos])

    grau_medio = sum(dict(G.degree()).values()) / G.number_of_nodes()
    densidade = nx.density(G)
    largest_cc = max(nx.connected_components(G), key=len)
    tamanho_maior_componente_conexo = len(largest_cc)
    porcentagem_maior_componente_conexo = ((tamanho_maior_componente_conexo / G.number_of_nodes()) * 100)
    transitividade = nx.transitivity(G)
    assortatividade = nx.degree_assortativity_coefficient(G)

    metricas = {
        'numero_de_arestas': num_arestas,
        'numero_de_nos': numero_de_nos,
        'diametro': diametro,
        'grau_medio': grau_medio,
        'densidade': densidade,
        'tamanho_de_maior_componente_conexo': tamanho_maior_componente_conexo,
        'porcentagem_maior_componente_conexo': porcentagem_maior_componente_conexo,
        'transitividade': transitividade,
        'assortatividade': assortatividade,
        'caminho_medio': caminho_medio
    }

    return metricas


# Função para exibir centralidades em ordem decrescente
def exibir_centralidades_ordenadas(centralidade_dict, nome_centralidade):
    centralidade_ordenada = dict(sorted(centralidade_dict.items(), key=lambda item: item[1], reverse=True))
    print(f"Centralidade de {nome_centralidade}:")
    for autor, valor in centralidade_ordenada.items():
        print(f"{autor}: {valor:.4f}")
    print()
# Função para desenhar o grafo com cores baseadas no número de publicações
def desenhar_grafo(G, sizes, publicacoes):
    pos = nx.spring_layout(G, k=0.5, iterations=50)

    # Determina a cor dos nós com base no número de publicações
    max_publicacoes = max(publicacoes.values())
    min_publicacoes = min(publicacoes.values())

    cmap_nodes = plt.get_cmap('coolwarm')
    node_colors = [publicacoes[node] for node in G.nodes()]

    plt.figure(figsize=(25, 25))

    # Função para ajustar pesos
    def ajustar_pesos(x, x_min, x_max):
        if x_max == x_min:
            return 1  # ou outro valor padrão adequado
        return ((x - x_min) / (x_max - x_min)) * 316

    # Desenha as arestas com cores diferentes baseadas no peso
    edge_weights = nx.get_edge_attributes(G, 'weight')
    x_min = min(edge_weights.values())
    x_max = max(edge_weights.values())

    # Ajustar os pesos das arestas
    edge_weights_ajustados = {edge: ajustar_pesos(weight, x_min, x_max) for edge, weight in edge_weights.items()}

    cmap_edges = plt.get_cmap('coolwarm')
    edge_colors_mapped = [cmap_edges(weight / 316) for weight in edge_weights_ajustados.values()]

    nx.draw_networkx_edges(G, pos, edgelist=edge_weights.keys(), edge_color=edge_colors_mapped, alpha=1)

    labels = {node: abreviacoes.get(node, node) for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size='large', font_weight='normal')

    nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color=node_colors, cmap=cmap_nodes, vmin=min_publicacoes, vmax=max_publicacoes, alpha=0.8)


    # Legenda para as cores das arestas
    sm_edges = plt.cm.ScalarMappable(cmap=cmap_edges, norm=mcolors.Normalize(vmin=1, vmax=316))
    sm_edges.set_array([])
    plt.colorbar(sm_edges, ax=plt.gca(), label='Peso das Coautorias', fraction=0.046, pad=0.04)

    plt.title('Grafo de Coautoria')
    plt.show()


# Função para criar o arquivo grafo.txt
def criar_arquivo_grafo(G, publicacoes):
    try:
        with open('grafoCC.txt', 'w', encoding='utf-8') as file:
            file.write('Vértices (Autores):\n')
            for autor, num_publicacoes in publicacoes.items():
                file.write(f'"{autor}": {num_publicacoes} publicações\n')

            file.write('\nArestas (Coautoria) e Pesos:\n')
            for u, v, data in G.edges(data=True):
                file.write(f'"{u}" - "{v}": {data["weight"]} coautorias\n')

        print('Arquivo grafo.txt criado com sucesso!')
    except Exception as e:
        print(f'Erro ao criar o arquivo grafo.txt: {e}')


# Leitura e Execução
def main():
    # Lê os arquivos CSV e TXT
    df_publicacoes = ler_csv('C:/Users/11941578900/Documents/GitHub/UDESC-SCRAPPING/Graph/UDESC-Network/Ciências_Contábeis/CienciasContabeisCurrículosFinal.csv')
    citacoes = ler_citacoes('C:/Users/11941578900/Documents/GitHub/UDESC-SCRAPPING/Graph/UDESC-Network/Ciências_Contábeis/CitacoesCC.txt')

    if df_publicacoes is None or df_publicacoes.empty or citacoes is None:
        print('Erro ao carregar os dados. Verifique os arquivos e tente novamente.')
        return

    # Cria o grafo de colaboração
    G = criar_grafo(df_publicacoes, citacoes)

    # Calcula as métricas de influência
    sizes, publicacoes = calcular_influencia(G, df_publicacoes, citacoes)

    # Calcula as métricas de centralidade
    degree_centrality, betweenness_centrality, closeness_centrality = calcular_centralidade(G)
    exibir_centralidades_ordenadas(degree_centrality, 'Grau')
    exibir_centralidades_ordenadas(betweenness_centrality, 'Intermediação')
    exibir_centralidades_ordenadas(closeness_centrality, 'Proximidade')

    # Calcula métricas adicionais
    metricas_adicionais = calcular_metricas_adicionais(G)

    # Exibe as métricas adicionais
    print('Métricas Adicionais:')
    for metrica, valor in metricas_adicionais.items():
        print(f'{metrica}: {valor}')

    # Desenha o grafo com cores baseadas no número de publicações
    desenhar_grafo(G, sizes, publicacoes)

    # Cria o arquivo grafo.txt
    # criar_arquivo_grafo(G, publicacoes)


# Executa a função principal
if __name__ == "__main__":
    main()
