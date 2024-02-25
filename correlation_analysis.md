# Documentação do Código de Análise Estatística

Este código realiza uma análise estatística para entender a relação entre as pontuações de impacto das manchetes do Wall Street Journal (WSJ) e várias métricas do índice VIX, salvando os resultados em um arquivo PDF.

## Importações de Bibliotecas

- `import pandas as pd`: Importa a biblioteca Pandas, usada para manipulação e análise de dados.
- `import sqlite3`: Importa a biblioteca sqlite3, usada para interagir com bancos de dados SQLite.
- `from scipy.stats import pearsonr, linregress`: Importa `pearsonr` e `linregress` da biblioteca scipy.stats, usadas para calcular o coeficiente de correlação de Pearson e realizar regressões lineares, respectivamente.
- `import matplotlib.pyplot as plt`: Importa a biblioteca matplotlib.pyplot para a geração de gráficos.
- `from matplotlib.backends.backend_pdf import PdfPages`: Importa `PdfPages` para salvar múltiplos gráficos em um único arquivo PDF.

## Definição de Variáveis Globais

- `DB = "headlines.db"`: Define o caminho do banco de dados SQLite contendo os dados das manchetes.
- `VIX_CSV = "VIX.csv"`: Define o caminho do arquivo CSV contendo os dados do índice VIX.

## Função `calculate_correlation_and_plot`

### Definição e Documentação

Define a função `calculate_correlation_and_plot` com dois parâmetros (`db_path`, `vix_csv_path`) e uma docstring explicativa.

### Conexão com o Banco de Dados e Carregamento de Dados

- **Conexão SQLite**: Abre uma conexão com o banco de dados SQLite especificado.
- **Consulta SQL e Carregamento**: Executa uma consulta SQL para selecionar dados das manchetes e carrega o resultado em um DataFrame do Pandas.
- **Fechamento da Conexão**: Fecha a conexão com o banco de dados.

### Preparação dos Dados das Manchetes

- **Conversão para Numérico**: Converte a coluna 'output' para valores numéricos, tratando erros com coerção.

### Carregamento e Preparação dos Dados do VIX

- **Carregamento do CSV**: Carrega os dados do VIX a partir de um arquivo CSV.
- **Conversão de Data**: Converte a coluna 'Date' para o formato datetime.

### Cálculo das Variações Percentuais Diárias do VIX

- **Cálculo de Variação Percentual**: Calcula a variação percentual diária para várias métricas do VIX e adiciona essas informações ao DataFrame.

### Fusão de Dados e Limpeza

- **Conversão de Data para Manchetes**: Converte a coluna 'ydm' do DataFrame das manchetes para datetime.
- **Fusão dos DataFrames**: Une os DataFrames das manchetes e do VIX com base nas datas.
- **Limpeza**: Remove linhas com valores NaN nas colunas relevantes.

### Plotagem e Salvamento dos Resultados

- **Inicialização do PDF**: Inicia um arquivo PDF para salvar os gráficos gerados.
- **Loop para Cada Métrica do VIX**: Itera sobre as métricas do VIX, calculando a correlação de Pearson e a regressão linear para cada uma, gerando gráficos com essas informações.
- **Geração de Gráficos**: Para cada métrica, gera um gráfico de dispersão dos dados e a linha de tendência da regressão linear, incluindo detalhes como o coeficiente de correlação, os valores p e legendas.
- **Salvamento no PDF**: Salva cada gráfico gerado no arquivo PDF.
- **Fechamento do Gráfico**: Fecha a figura atual para evitar sobreposições.

## Função `main`

- **Definição da Função `main`**: Define uma função `main` que chama `calculate_correlation_and_plot` com os caminhos do banco de dados e do arquivo CSV como argumentos.

## Execução Condicional

Verifica se o script está sendo executado como um programa principal e, em caso afirmativo, chama a função `main`.

Este script é um exemplo completo de análise de dados, desde a leitura e preparação dos dados até a análise estatística e a visualização dos resultados.
