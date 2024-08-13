### Análise de Coautoria na UDESC-CEAVI
Este projeto visa analisar redes de coautoria no campus CEAVI da UDESC, utilizando dados extraídos da plataforma Lattes. O processo envolve a manipulação de arquivos CSV para gerar grafos de colaboração e aplicar métricas relevantes.

### Estrutura do Projeto
* Converter.py: Algoritmo responsável por converter arquivos CSV que não seguem a formatação esperada para o formato compatível com a geração de grafos.

* Eliminate.py: Algoritmo que elimina ou ajusta dados inconsistentes nos CSVs, garantindo que estejam prontos para serem processados.

* Graph_Final.py: Script principal que gera os grafos de coautoria a partir dos CSVs formatados e aplica as métricas de análise definidas no trabalho.

### Como Utilizar
 1. Pré-processamento dos CSVs:

* Execute Converter.py para garantir que os CSVs estejam no formato adequado.
* Execute Eliminate.py para limpar e ajustar quaisquer inconsistências nos dados.
 2. Geração e Análise dos Grafos:

Após o pré-processamento, utilize Graph_Final.py para gerar os grafos e aplicar as métricas desejadas.
