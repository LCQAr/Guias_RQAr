"""
Webscraping de dados de qualidade do ar da CETREL (Bahia).

Objetivo
--------
Coletar dados horários de qualidade do ar disponibilizados pela CETREL,
organizar os registros em formato tabular e exportar arquivos CSV separados
por estação de monitoramento e poluente.

Arquivos e recursos necessários
-------------------------------
- Conexão com a internet;
- Acesso ao endpoint da CETREL:
  https://www.cetrel.com.br/wp-admin/admin-ajax.php
- Permissão de escrita no diretório definido em `output_dir`.

Saídas geradas
--------------
- Arquivos CSV contendo séries temporais horárias de concentração de poluentes;
- Um arquivo para cada combinação de estação de monitoramento e poluente.

Observações
-----------
- O script realiza consultas horárias para todo o período configurado;
- O volume de requisições e arquivos gerados pode ser elevado para períodos longos;
- Recomenda-se testar inicialmente períodos reduzidos antes da execução completa.

Criado por Leonardo Hoinaski
"""

# ---------------------------------- Importação de pacotes ----------------------------------
import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import calendar
import os

# Target URL
# Conferir se a URL está acessível e se o endpoint não mudou. Caso haja alterações, atualizar a URL.
url = "https://www.cetrel.com.br/wp-admin/admin-ajax.php"

# Headers
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded"
}

# Função para buscar dados de um horário
def fetch_data(horario: str):
    payload = {
        "action": "integration",
        "horario": horario
    }
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=20)
        response.raise_for_status()
        raw_text = str(response.text).lstrip("\ufeff")  # ✅ limpa BOM
        return raw_text
    except Exception as e:
        print(f"❌ Error fetching {horario}: {e}")
        return None

# Pasta de saída
'''  >>> CONFIGURAÇÃO OBRIGATÓRIA <<<
Ajuste este caminho para o diretório de saída no seu computador antes de executar o script. 
Como o código é compartilhado via Git, este diretório varia entre usuários. 
Certifique-se de que o caminho exista e que você tenha permissão de escrita. '''
output_dir = "/home/nobre/Notebooks/RQAR_2025_book/data/BA/output_by_station_pollutant"
os.makedirs(output_dir, exist_ok=True)

# Loop pelos anos, meses e dias
# Alterar o intervalo de anos conforme necessário
for year in range(1988, 2026):
    print('------------------ '+str(year)+' ------------------')
    
    for month in range(1, 13):
        days = calendar.monthrange(year, month)[1]
        
        for day in range(1, days+1):
            print(str(day)+'/'+str(month))
            start_time = datetime(year, month, day, 0, 0, 0)
            end_time = datetime(year, month, day, 23, 0, 0)
            
            # Horários horários do dia
            horarios = []
            current = start_time
            while current <= end_time:
                horarios.append(current.strftime("%Y-%m-%d %H:%M:%S"))
                current += timedelta(hours=1)
            
            # Coleta os dados
            results = []
            for h in horarios:
                print(f"Fetching data for {h} ...")
                data = fetch_data(h)
                if data:
                    results.append(data)
            
            # Processa todos os raw_texts
            dfs = []
            for raw_text in results:
                try:
                    data_json = json.loads(raw_text)
                    stations = data_json["data"]
                    df_temp = pd.DataFrame(stations)
                    dfs.append(df_temp)
                except Exception as e:
                    print(f"❌ Error parsing JSON: {e}")
            
            if not dfs:
                continue
            
            df = pd.concat(dfs, ignore_index=True)
            
            # Seleciona colunas relevantes
            concentration_cols = [
                "DATA_REFERENCIA", "ESTACAO", "LOCAL",
                "CONCENT_SO2", "VALIDOS_SO2",
                "CONCENT_NO2", "VALIDOS_NO2",
                "CONCENT_O3", "VALIDOS_O3",
                "CONCENT_CO", "VALIDOS_CO",
                "CONCENT_PI", "VALIDOS_PI",
                "CONCENT_PI_25", "VALIDOS_PI_25"
            ]
            df = df[concentration_cols]
            
            # Converte strings numéricas para float
            for col in df.columns:
                if col.startswith("CONCENT_") or col.startswith("VALIDOS_"):
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            
            # Transformar para formato longo
            value_cols = ["SO2", "NO2", "O3", "CO", "PI", "PI_25"]
            pol_ids = ["003","004","005","007","001","002"]
            
            df_long = pd.DataFrame()
            
            for ii,pol in enumerate(value_cols):
                temp = df[[
                    "DATA_REFERENCIA", "ESTACAO", "LOCAL",
                    f"CONCENT_{pol}", f"VALIDOS_{pol}"
                ]].copy()
                temp.columns = ["DATETIME", "ESTACAO", "LOCAL", "CONC", "QAQC"]
                temp["POLUENTE"] = pol_ids[ii]
                df_long = pd.concat([df_long, temp], ignore_index=True)
            
            # Criar CSVs separados por estação e poluente
            for (station, pollutant), group in df_long.groupby(["ESTACAO", "POLUENTE"]):
                filename = f"BA_{station}_{pollutant}_{year}_{month}_{day}.csv".replace(" ", "_")
                filepath = os.path.join(output_dir, filename)
                group = group.drop(['POLUENTE',"ESTACAO", 'LOCAL'], axis=1)
                group.to_csv(filepath, index=False, encoding="utf-8")
                print(f"✅ Saved: {filepath}")

            
        #df.to_csv("cetrel_data.csv", index=False, encoding="utf-8")
