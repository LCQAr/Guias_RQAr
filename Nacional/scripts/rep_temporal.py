# %%
# #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 14 13:48:06 2025

@author: lcqar

Este script avalia a representatividade temporal dos dados de poluentes,
verificando se cada período (dia, mês, quadrimestre ou ano) possui uma
quantidade mínima de medições válidas para ser considerado representativo,
de acordo com os critérios do MMA.
"""

# %% Imports

import pandas as pd
import os
import numpy as np

os.chdir('/home/nobre/Notebooks/RQAR_2025_book/')


# %% Configuração dos critérios de representatividade temporal

# Cria uma tabela contendo, para cada poluente, os critérios utilizados
# para determinar a representatividade temporal dos dados.

# ====POLUENTES:
#   Identifica o poluente ao qual os critérios se aplicam.
#
# ====DIA:
#   Define qual tipo de dado diário deve ser utilizado:
#   - '24': utiliza a média das 24 horas do dia;
#   - '8': utiliza a maior média móvel de 8 horas;
#   - '1': utiliza o maior valor horário do dia;
#   - '' : utiliza o maior valor horário do dia como regra padrão.
#
# === MES:
#   Define o critério de representatividade mensal.
#   'mensal' corresponde ao cálculo da média mensal;
#   'mensal_geom' corresponde à estrutura utilizada para PTS.
#
# ==== ANO:
#   Define o critério de representatividade anual.
#   'anual' corresponde ao cálculo anual;
#   'anual_geom' corresponde à estrutura específica de PTS.

df_rep_temporal = pd.DataFrame({
    'POLUENTES': ['MP10','MP25','SO2','NO2','O3','FMC','CO','PTS','Pb'],
    'DIA': ['24','24','24','1','8','24','8','24',''],
    'MES': ['mensal','mensal','mensal','mensal','mensal','mensal','mensal','mensal_geom','mensal'],
    'ANO': ['anual','anual','anual','anual','anual','anual','anual','anual_geom','anual']
}).set_index("POLUENTES")

def rep_temp(df,agrupamento,criterio,periodo_ref):
"""
Avalia a representatividade temporal dos dados dentro de cada
grupo de tempo.

Definições dos parametros:
- agrupamento : list
        Colunas utilizadas para definir o período que será avaliado.
        Exemplos:
        ['ANO', 'MES', 'DIA'] -> avaliação diária;
        ['ANO', 'MES']        -> avaliação mensal.
        
- criterio : str
        Define a unidade temporal utilizada para verificar a quantidade
        mínima de dados disponíveis.
        - 'HORA': verifica quantidade de horas disponíveis;
        - 'DIA': verifica quantidade de dias disponíveis.
        
- periodo_ref : str ou função
        Define como será calculado o valor representativo do período.
        Pode ser:
        - '8' -> maior média móvel de 8 horas;
        - uma função estatística, como np.mean ou np.max

"""
    resultados = []
    # Agrupa os dados de acordo com o período por critérios
    for chave, dados in df.groupby(agrupamento):

         # Conta quantidade de valores medidos válidos
        qntd_valor = dados['VALOR'].notna().sum()  

        # Define a quantidade total de registros esperados para o período
        if criterio == 'HORA':

            # Para uma avaliação diária baseada em horas,
            # são esperadas 24 horas
            qntd_tempo = 24
        elif criterio == 'DIA':

            # Para uma avaliação mensal baseada em dias,
            # determina a quantidade de dias do mês.
            # chave[0] = ano
            # chave[1] = mês
            if chave[1] in [4,6,9,11]:
                qntd_tempo = 30
            elif chave[1] in [1,3,5,7,8,10,12]:
                qntd_tempo = 31
            else: # Fevereiro possui 29 dias em anos bissextos
                if (chave[0] % 4 == 0 and chave[0] % 100 != 0) or (chave[0] % 400 == 0):
                    qntd_tempo = 29
                else:
                    qntd_tempo = 28
        # Verifica se o período possui pelo menos 2/3 dos dados esperados.
        # Para uma avaliação diária:
        #   2/3 de 24 horas = 16 horas.
        # Para uma avaliação mensal:
        #   2/3 do número de dias do mês.
        if qntd_valor >= (2/3) * qntd_tempo:
#            # Calcula o valor representativo do período somente quando
            # a quantidade mínima de dados foi atingida.
            if periodo_ref == "8":      
                 # Calcula médias móveis de 8 horas.
                # São necessárias pelo menos 6 observações dentro da
                # janela de 8 horas para calcular uma média.
                #
                # O maior valor entre as médias móveis é utilizado
                # como valor representativo do dia.
                media = dados["VALOR"].rolling(window=8, min_periods=6).mean().max()
            else:
                # Se periodo_ref for uma função, é aplicada diretamente aos valores do período.
                media = periodo_ref(dados["VALOR"])

                
            rep = True # O período é considerado representativo
        else:
            media = np.nan # Caso não exista quantidade suficiente de dados, não é um valor representativo   
            rep = False

        # Calcula o percentual de dados disponíveis no período
        prcnt = 100*qntd_valor/qntd_tempo

        # Armazena:
        # - identificação do período;
        # - valor representativo;
        # - indicador de representatividade;
        # - percentual de dados disponíveis.
        resultados.append((*chave, media, rep, prcnt))

    return resultados

def conta_dias_quadrimestre(ano,quadrimestre):
"""
Determina a quantidade de dias existente em cada quadrimestre.
O cálculo considera anos bissextos porque o primeiro quadrimestre
contém janeiro, fevereiro, março e abril.

Definição de Parâmetros:
- quadrimestre : int
        Quadrimestre analisado:
        1 -> janeiro a abril;
        2 -> maio a agosto;
        3 -> setembro a dezembro.
"""

    if quadrimestre == 1:
        # Janeiro + fevereiro + março + abril.
        # Fevereiro possui 29 dias em anos bissextos.
        if (ano % 4 == 0 and ano % 100 != 0) or (ano % 400 == 0):
            dias = 121
        else:
            dias = 120
    elif quadrimestre == 2: # Maio + junho + julho + agosto.
        dias = 123
    else: # Setembro + outubro + novembro + dezembro.
        dias = 122

    return dias

def rep_temp_ano(df,agrupamento,criterio):
"""
Avalia a representatividade temporal de cada quadrimestre.
O período é considerado representativo quando possui pelo menos metade dos dias esperados com dados válidos.

Definição de Parâmetros:
- agrupamento : list
        Colunas utilizadas para separar os dados por ano e quadrimestre.

- criterio : str
        Critério temporal utilizado. Neste script é utilizado
        para identificar que a análise é realizada por quadrimestre.
"""
    resultados = []
    # Separa os dados por ano e quadrimestre.
    for chave, dados in df.groupby(agrupamento):
        # Conta quantidade de valores medidos válidos
        qntd_valor = dados['VALOR'].notna().sum()
        # Determina quantos dias existem no quadrimestre analisado
        qntd_tempo = conta_dias_quadrimestre(chave[0],chave[1])         

        # O quadrimestre é representativo quando possui pelo menos
        # metade dos dias esperados com dados válidos.
        if qntd_valor >= (1/2) * qntd_tempo:
            rep = True
        else:
            rep = False
    
        resultados.append((*chave, rep))

    return resultados
# %% Processamento da representatividade temporal

# Cria o DataFrame que irá armazenar o resumo da representatividade
# temporal de cada estação.
df_estacoes_rep_temporal = pd.DataFrame({
                    'ID_MMA_COMPLETO':[],
                    'PRCNT_REP_TEMPORAL_DIARIA':[],
                    'PRCNT_REP_TEMPORAL_MENSAL':[],
                    'PRCNT_REP_TEMPORAL_ANUAL':[]
                })		
# Percorre todos os poluentes definidos na tabela de critérios                
for pol in df_rep_temporal.index:
    # Define o caminho da pasta que contém os arquivos do poluente
    path = os.getcwd()+'/data/MQAr_new/' + pol + '/'

    print(pol)
    # Verifica se a pasta existe e se contém arquivos
    if os.path.isdir(path) and os.listdir(path):
        # Lista os arquivos existentes na pasta do poluente
        arquivos = os.listdir(path)
        # Percorre os arquivos de cada estação
        for estacao in arquivos:
            # Garante que o arquivo é .csv
            if estacao.endswith('.csv'):

                print(estacao)

                df = pd.read_csv(path+estacao)
                # Garante que a coluna VALOR esteja em formato numérico
                df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce")


                # == REPRESENTATIVIDADE DIÁRIA — BASE HORÁRIA ==
                # Agrupa os dados por ano, mês e dia.
                # O critério 'HORA' faz com que a função verifique a existência de pelo menos 2/3 das 24 horas.
                resultados_24 = rep_temp(df,['ANO','MES','DIA'],'HORA',np.mean)
                 # Converte os resultados para um DataFrame
                df_24 = pd.DataFrame(resultados_24, columns=['ANO', 'MES', 'DIA', 'VALOR', 'REP_DIA','PRCNT_HORAS_DIA_REP_TEMPORAL'])
                # Cria uma data representando cada dia
                df_24['DATETIME'] = pd.to_datetime(
                        dict(year=df_24["ANO"], month=df_24["MES"], day=df_24["DIA"])
                    )
                 # Organiza as colunas do DataFrame diário
                df_24 = df_24[['DATETIME','ANO','MES','DIA','VALOR','REP_DIA','PRCNT_HORAS_DIA_REP_TEMPORAL']]
                 # =====================================================
                # DEFINIÇÃO DO VALOR DIÁRIO DO POLUENTE
                # =====================================================

                # Para poluentes cujo critério diário é '24', utiliza diretamente a média diária calculada em df_24.
                if df_rep_temporal['DIA'][pol] == '24':
                    df_dia = df_24
                # Para poluentes cujo critério diário é '8', calcula a maior média móvel de 8 horas do dia.
                elif df_rep_temporal['DIA'][pol] == '8':
                    resultados_dia = rep_temp(df,['ANO','MES','DIA'],'HORA','8')
                    # Cria o DATETIME correspondente ao dia
                    df_dia = pd.DataFrame(resultados_dia, columns=['ANO', 'MES', 'DIA', 'VALOR', 'REP_DIA','PRCNT_HORAS_DIA_REP_TEMPORAL'])

                    df_dia['DATETIME'] = pd.to_datetime(dict(year=df_dia["ANO"], month=df_dia["MES"], day=df_dia["DIA"]))

                    df_dia = df_dia[['DATETIME','ANO','MES','DIA','VALOR','REP_DIA','PRCNT_HORAS_DIA_REP_TEMPORAL']]
                        
                else: # Para os demais critérios diários, utiliza o maior valor horário do dia.
                    resultados_dia = rep_temp(df,['ANO','MES','DIA'],'HORA',np.max)

                    df_dia = pd.DataFrame(resultados_dia, columns=['ANO', 'MES', 'DIA', 'VALOR', 'REP_DIA','PRCNT_HORAS_DIA_REP_TEMPORAL'])

                    df_dia['DATETIME'] = pd.to_datetime(dict(year=df_dia["ANO"], month=df_dia["MES"], day=df_dia["DIA"]))

                    df_dia = df_dia[['DATETIME','ANO','MES','DIA','VALOR','REP_DIA','PRCNT_HORAS_DIA_REP_TEMPORAL']]
# Salva o .csv
                df_dia.to_csv(os.getcwd()+'/data/MQAr_averages_new2/'+df_rep_temporal['DIA'][pol]+'/'+pol+'/'+estacao,index=False)
                # =====================================================
                # REPRESENTATIVIDADE MENSAL
                # =====================================================

                # Utiliza os valores diários calculados anteriormente
                # para determinar a representatividade de cada mês.
                # Um mês precisa possuir pelo menos 2/3 dos dias
                # esperados com dados válidos 
                resultados_mes = rep_temp(df_24,['ANO','MES'],'DIA',np.mean)
                # Representa o mês pelo primeiro dia do mês
                df_mes = pd.DataFrame(resultados_mes, columns=['ANO', 'MES', 'VALOR', 'REP_MES','PRCNT_DIAS_MES_REP_TEMPORAL'])

                df_mes['DATETIME'] = pd.to_datetime(dict(year=df_mes["ANO"], month=df_mes["MES"], day=1))
            
                df_mes = df_mes[['DATETIME','ANO','MES','VALOR','REP_MES','PRCNT_DIAS_MES_REP_TEMPORAL']]

                df_mes.to_csv(os.getcwd()+'/data/MQAr_averages_new2/'+df_rep_temporal['MES'][pol][:6]+'/'+pol+'/'+estacao,index=False)
                # Transforma os percentuais de representatividade mensal em uma tabela onde: linhas  -> anos; colunas -> meses; valores -> percentual de dias representativos no mês
                df_mes_ano = df_mes.pivot(index='ANO', columns='MES', values='PRCNT_DIAS_MES_REP_TEMPORAL')
                                # Garante que os meses estejam em ordem crescente.
                df_mes_ano = df_mes_ano.reindex(sorted(df_mes_ano.columns), axis=1)
                
                df_mes_ano = df_mes_ano.reset_index()
                        
                df_mes_ano.to_csv(os.getcwd()+'/data/MQAr_averages_new2/rep_temporal_mes_ano/'+pol+'/'+estacao,index=False)
                # Define os três quadrimestres utilizados na avaliação anual: 1 -> janeiro a abril;  2 -> maio a agosto; 3 -> setembro a dezembro
                condicoes = [
                    (df_dia['MES'] <= 4),
                    (df_dia['MES'] >= 5) & (df_dia['MES'] <= 8),
                    (df_dia['MES'] >= 9)
                ]
                # Cria a coluna QUADRIMESTRE de acordo com o mês
                quadrimestre = [1, 2, 3]
                
                df_dia['QUADRIMESTRE'] = np.select(condicoes, quadrimestre)
                # Avalia cada quadrimestre separadamente
                resultados_quad = rep_temp_ano(df_dia,['ANO','QUADRIMESTRE'],'QUADRIMESTRE')
                # Agrupa os resultados dos três quadrimestres por ano.
                # O ano somente será considerado representativo quando os três quadrimestres forem representativos
                df_quad = pd.DataFrame(resultados_quad, columns=['ANO', 'QUADRIMESTRE', 'REP_QUAD'])

                
                df_ano_quad = df_quad.groupby("ANO", as_index=False).agg({"REP_QUAD": lambda x: x.sum() == 3})

                resultados = []
                # == CÁLCULO DA REPRESENTATIVIDADE ANUAL ==
                # Agrupa os dados diários por ano
                for ano, dados in df_24.groupby(['ANO']):

                    # Conta a quantidade de dias com dados válidos
                    qntd_valor = dados['VALOR'].notna().sum()

                    # Define a quantidade de dias do ano, considerando anos bissextos.
                    if (ano[0] % 4 == 0 and ano[0] % 100 != 0) or (ano[0] % 400 == 0):
                        dias = 366
                    else:
                        dias = 365
                    # Calcula o percentual de dias do ano com dados válidos
                    prcnt_rep_dias = (100*qntd_valor/dias)

                    # Conta quantos meses possuem valores válido
                    qntd_meses = df_mes.groupby(['ANO']).get_group(ano[0])['VALOR'].notna().sum()

                    # Calcula o percentual de meses do ano com dados
                    prcnt_rep_meses = (100*qntd_meses/12)

                    # O ano só recebe um valor representativo quando os três quadrimestres foram considerados representativos
                    if df_ano_quad.loc[df_ano_quad["ANO"] == ano[0], "REP_QUAD"].values[0] == True:
                        # Calcula a média dos valores diários do ano
                        media = dados['VALOR'].mean()
                        rep = True
                    else:
                        media = np.nan
                        rep = False
                    resultados.append((*ano, media, rep, prcnt_rep_dias, prcnt_rep_meses))
                # Cria o DataFrame com os resultados anuais
                df_ano = pd.DataFrame(resultados, columns=['ANO', 'VALOR','REP_TEMPORAL_ANUAL','PRCNT_DIAS_ANO_REP_TEMPORAL','PRCNT_MESES_ANO_REP_TEMPORAL'])
                # Representa cada ano pelo dia 1º de janeiro
                df_ano['DATETIME'] = pd.to_datetime(dict(year=df_ano["ANO"], month=1, day=1))
            
                df_ano = df_ano[['DATETIME','ANO','VALOR','REP_TEMPORAL_ANUAL','PRCNT_DIAS_ANO_REP_TEMPORAL','PRCNT_MESES_ANO_REP_TEMPORAL']]

                df_ano.to_csv(os.getcwd()+'/data/MQAr_averages_new2/'+df_rep_temporal['ANO'][pol][:5]+'/'+pol+'/'+estacao, index=False)

                # =====================================================
                # RESUMO DA REPRESENTATIVIDADE DA ESTAÇÃO
                # =====================================================

                # Calcula o percentual de dias representativos disponíveis no conjunto de dados diário da estação
                prcnt_dia = 100 * df_dia['VALOR'].notna().sum() / len(df_dia)
                # Calcula o percentual de meses representativos
                prcnt_mes = 100 * df_mes['VALOR'].notna().sum() / len(df_mes)
                # Calcula o percentual de anos representativos
                prcnt_ano = 100 * df_ano['VALOR'].notna().sum() / len(df_ano)

                 # Cria uma lista contendo todos os anos monitorados pela estação
                anos = df_ano['ANO'].astype(int).astype(str).str.cat(sep=',')
                # Seleciona somente os anos que possuem valor anual representativo
                df_anos_rep = df_ano.dropna(subset=['VALOR'])
                # Cria uma lista contendo somente os anos representativos
                anos_representativos = df_anos_rep['ANO'].astype(int).astype(str).str.cat(sep=',')

                # Cria um resumo da estação: ID_MMA_COMPLETO, percentuais de representatividade diária, mensal e anual, anos representativos e todos os anos monitorados
                prcnt_estacao = {'ID_MMA_COMPLETO': estacao[:-4], 
                                 'PRCNT_REP_TEMPORAL_DIARIA': prcnt_dia, 
                                 'PRCNT_REP_TEMPORAL_MENSAL': prcnt_mes, 
                                 'PRCNT_REP_TEMPORAL_ANUAL': prcnt_ano, 
                                 'ANOS_REPRESENTATIVOS':anos_representativos,
                                 'ANOS_MONITORADOS': anos}
                # Adiciona o resumo da estação ao DataFrame geral
                df_estacoes_rep_temporal = pd.concat([df_estacoes_rep_temporal, pd.DataFrame([prcnt_estacao])], ignore_index=True)
                # Salva .csv    
                df_estacoes_rep_temporal.to_csv(os.getcwd()+'/data/MQAr_averages/REP_TEMPORAL.csv', index=False)
