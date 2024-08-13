### Análise de Coautoria na UDESC-CEAVI
Este projeto visa analisar redes de coautoria no campus CEAVI da UDESC, utilizando dados extraídos da plataforma Lattes. O processo envolve a manipulação de arquivos CSV para gerar grafos de colaboração e aplicar métricas relevantes.

### Estrutura do Projeto
* Converter.py: Algoritmo que remove os espaços dos arquivos CSV que estão em tuplas e adiciona o padrão "", "" para formatar os dados corretamente.

* Eliminate.py: Algoritmo que elimina inconsistências nos CSVs após o pré-processamento realizado pelo Converter.py, garantindo que os dados estejam prontos para análise.

* Graph_Final.py: Script principal que gera os grafos de coautoria a partir dos CSVs formatados e aplica as métricas de análise definidas no trabalho.

### Como Utilizar
 1. Pré-processamento dos CSVs:

* Execute Converter.py para garantir que os CSVs estejam no formato adequado, tirando das tuplas e separando .
* Execute Eliminate.py para limpar e ajustar quaisquer inconsistências nos dados.
 2. Geração e Análise dos Grafos:

Após o pré-processamento, utilize Graph_Final.py para gerar os grafos e aplicar as métricas desejadas.
