import pandas as pd

# Caminho do arquivo CSV
file_path = 'EngenhariaCivilCurrículos.csv'
output_file_path = 'EngenhariaCivilCurrículosFinal.csv'


# Ler o arquivo CSV como texto
with open(file_path, 'r', encoding='utf-8') as file:
    data = file.readlines()

# Função para corrigir as linhas com 8 elementos
def correct_line(line):
    elements = line.split(',')
    if len(elements) == 8:
        elements = [el for el in elements if el]  # Remover elementos vazios
    return ','.join(elements)

# Substituir ",," por "," em cada linha e corrigir linhas com 8 elementos
data_modified = [correct_line(line.replace(',,', ',')) for line in data]

# Salvar o arquivo modificado
with open(output_file_path, 'w', encoding='utf-8') as file:
    file.writelines(data_modified)

print(f'O arquivo modificado foi salvo em {output_file_path}')