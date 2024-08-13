# Tem que ser melhorado, pois tem que revisar na mão, está adicionando, em alguns casos, está adicionando "" ou , onde não era para adicionar
def process_content(content):
    processed_lines = []
    #Cabeçalho
    header = '"Tipo","AutorPrincipal","Ano","URLDOI","Título","Periódico/Conferêncial","Coautores"'
    processed_lines.append(header)
    for line in content:
        #Remover espaços extras e substituir tabulações por vírgulas
        columns = line.strip().split('\t')

        #Certificar-se de que temos 7 colunas, adicionando colunas vazias se necessário
        while len(columns) < 7:
            columns.append('')

        #Adicionar aspas em torno de cada coluna
        quoted_columns = []
        for i, col in enumerate(columns):
            # Tratamento especial para a coluna URLDOI
            if i == 3 and col == "":
                quoted_columns.append('')  # Coluna vazia sem aspas
            else:
                quoted_columns.append(f'"{col}"')

        # Reunir as colunas processadas em uma linha
        processed_line = ','.join(quoted_columns)
        processed_lines.append(processed_line)
    return processed_lines


#arquivo original
file_original = 'teste-04-EC-publicacoesPorMembro.csv'

#conteúdo do arquivo original
with open(file_original, 'r', encoding='utf-8') as file:
    content = file.readlines()

processed_content = process_content(content)

processed_file_path = 'EngenhariaCivilCurrículos.csv'

with open(processed_file_path, 'w', encoding='utf-8') as file:
    for line in processed_content:
        file.write(line + '\n')

print(f'Arquivo processado salvo em: {processed_file_path}')
