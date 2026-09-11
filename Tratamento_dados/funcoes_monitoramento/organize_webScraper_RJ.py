#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


Criado por Leonardo Hoinaski
"""

# ---------------------------------- Importação de pacotes ----------------------------------

import os 
import pandas as pd
import numpy as np
import glob

def tratar_dados(df):
    """
    Recebe DataFrame cru, cria coluna datetime, converte e limpa valores.
    Retorna DataFrame com índice datetime e coluna 'Valor' em float, valores < 0 viram NaN.

    Parameters
    ----------
    df : TYPE
        DF contendo dados brutos com colunas, sem coluna de datetime .

    Returns
    -------
    df : TYPE
        DataFrame tratado com indice de datetime e valores numéricos prontos para análise.

    """
    time_range = pd.date_range(df['DATETIME'].min(), df['DATETIME'].max(), freq='h').to_series(name='DATETIME')
    df = pd.merge(time_range, df,how='left')
    #df = df.set_index('datetime', drop=False)
    df['DATETIME'] = pd.to_datetime(df['DATETIME']).copy()
    return df

# CORRIGIDO (4): algumas datas vêm no formato 'dd-mon-yyyy HH:MM' com o mês
# abreviado em português (ex: '01-fev-2025 00:00'). pd.to_datetime (mesmo com
# format='mixed') só reconhece abreviações em inglês, e lançava DateParseError.
# Esta função traduz o mês pt->numérico antes de parsear, mantendo os demais
# formatos (já numéricos/ISO) intactos.
MESES_PT = {
    'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04',
    'mai': '05', 'jun': '06', 'jul': '07', 'ago': '08',
    'set': '09', 'out': '10', 'nov': '11', 'dez': '12',
}

def parse_datetime_misto(series):
    """
    Converte uma coluna de datas em formatos mistos (incluindo 'dd-mon-yyyy HH:MM'
    com mês abreviado em português) para datetime.
    """
    s = series.astype(str)
 
    def _troca_mes(match):
        dia, mes, ano = match.group(1), match.group(2).lower(), match.group(3)
        num_mes = MESES_PT.get(mes, mes)
        return f"{dia}-{num_mes}-{ano}"
 
    # Só mexe nas strings que batem com o padrão dd-<mes_abreviado_letras>-yyyy;
    # o resto (formatos já numéricos/ISO) passa direto sem alteração.
    s = s.str.replace(r'(\d{1,2})-([A-Za-zçÇ]{3})-(\d{4})', _troca_mes, regex=True)
 
    return pd.to_datetime(s, format='mixed', dayfirst=True)

    
year = 2025
category = "auto" #auto ; semiauto
directory_path = f'/home/nobre/Notebooks/RQAr/dados/dados_brutos/{year}/RJ/dados_coletados/{category}/'
directory_out = f'/home/nobre/Notebooks/RQAr/dados/dados_formatados/{year}/monitoramento/RJ/'

station_parameters_dict = {
    'CH4 - Metano [ppm]': '7',
    'CO - Monóxido de Carbono [ppm]': '3',
    'NOX - Óxidos de Nitrogênio [µg/m³]': '9',
    'HCNM - Hidrocarbonetos Não-Metano [ppm]': '11',
    'MP10 - Partículas Inaláveis (<10µm) [µg/m³]': '18',
    'MP2,5 - Partículas Inaláveis (<2,5µm) [µg/m³]': '20',
    'SO2 - Dióxido de Enxofre [µg/m³]': '23',
    'BENZ - Benzeno [µg/m³]': '134',
    'ETBENZ - Etil Benzeno [µg/m³]': '263',
    'OX - O-Xileno [µg/m³]': '413',
    'TOL - Tolueno [µg/m³]': '482',
    'XIL - Xileno [µg/m³]': '504',
    'H2S - Sulfeto de Hidrogênio [µg/m³]': '1305',
    'NO2 - Dióxido de Nitrogênio [µg/m³]': '1465',
    'PTS - Partículas Totais em Suspensão [µg/m³]': '1955',
    'NO - Monóxido de Nitrogênio [µg/m³]': '2128',
    'O3 - Ozônio [µg/m³]': '2130',
    'HCT - Hidrocarbonetos Totais [ppm]': '2143',
    'MPX - M,P-Xileno [µg/m³]': '2168',
    'DV - Direção do Vento [°]': '100001',
    'DVDP - Desvio Padrão Dir. Vento [°]': '20051',
    'PA - Pressão Atmosférica [hPa]': '100007',
    'PP - Precipitação [mm]': '100004',
    'RS - Radiação Solar [W/m²]': '100006',
    'TA - Temperatura do Ar [°C]': '100002',
    'UR - Umidade Relativa [%]': '100005',
    'VV - Velocidade do Vento [m/s]': '100000'
}

stations_dict = {
    12: "RJ - Largo do Bodegão",
    18: "BR - São Bernardo",
    19: "NI - Monteiro Lobato",
    20: "RJ - Campo dos Afonsos",
    21: "RJ - Taquara",
    22: "RJ - Centro",
    23: "RJ - Engenhão",
    24: "RJ - Gericinó",
    25: "RJ - Lagoa",
    26: "RJ - Lourenço Jorge",
    27: "SG - UERJ",
    28: "NI - Meteorológica Cerâmica",
    29: "RJ - Manguinhos",
    30: "DC - Campos Elíseos",
    31: "DC - Jardim Primavera",
    32: "DC - São Bento",
    33: "DC - Vila São Luiz",
    34: "DC - Pilar",
    35: "DC - Meteorológica Jardim Piratininga",
    36: "RJ - Ilha de Paquetá",
    37: "RJ - Ilha do Governador",
    38: "Itb - Porto das Caixas",
    39: "Itb - Sambaetiba",
    40: "Itb - Areal",
    41: "Itb - Apa Guapimirim",
    42: "Itb - Fazenda Macacu",
    43: "Mc - Cabiúnas",
    44: "Mc - Fazenda Severina",
    45: "Mc - Pesagro",
    46: "Mc - Meteorológica Fazenda Severina",
    47: "Mc - Fazenda Airis",
    48: "SJB - Mato Escuro 5º D2istrito",
    49: "SJB - Açú 5º Distrito",
    50: "Cg - Val Palmas",
    51: "Cg - Macuco",
    52: "Cg - Meteorológica Euclidelândia 2",
    53: "Cg - Meteorológica Euclidelândia 1",
    54: "Cg - Euclidelândia",
    55: "Jp - Engenheiro Pedreira",
    56: "Sp - Meteorológica Jardim Maracanã",
    57: "NI - Jardim Guandu",
    58: "Sp - Piranema",
    59: "RJ - Meteorológica UTE Santa Cruz",
    60: "Itg - Monte Serrat",
    61: "RJ - Adalgisa Nery",
    62: "RJ - Meteorológica Santa Cruz",
    63: "Itg - Coroa Grande",
    64: "Mt - Itacuruçá",  # 2013
    65: "Itg - Meteorológica Ilha Da Madeira",
    66: "Itg - Ilha Da Madeira",
    67: "Mt - Ibicuí",  # 2013
    68: "Mt - Praia Do Saco",  # 2013
    69: "VR - Belmonte",
    70: "VR - Retiro",
    71: "VR - Santa Cecília",
    72: "VR - Meteorológica Ilha das Águas Cruas",
    73: "BM - Boa Sorte",
    74: "BM - Sesi",
    75: "BM - Bocaininha",
    76: "BM - Roberto Silveira",
    77: "BM - Vista Alegre",
    78: "PR - Porto Real",
    79: "Qt - Bom Retiro",
    80: "Rs - Casa da Lua",
    81: "Rs - Cidade Alegria",
    82: "Itt - Campo Alegre",
    83: "Itt - Meteorológica Itatiaia",
    85: "Mt - Sahy",  # 2013
    86: "SJB - Fazenda Saco Dantas",
    142: "Mc - Imboassica",
    215: "SJM - Coelho da Rocha",
    216: "SC - João XXIII (Caminhao)",
    217: "SC - 27ºBPM (Caminhão)",
    218: "RJ - Van (Sumaré-SBT)",
    219: "RJ - Van (Parque Parnaso - Guapimirim)",
    220: "RJ - Van (Parque do Mendanha)",
    221: "RJ - Van (Parque da Serra da Tiririca)",
    222: "RJ - Urca",
    223: "RJ - São Conrado",
    224: "RJ - Maracanã",
    225: "RJ - Leblon",
    226: "RJ - Lab. INEA",
    227: "RJ - Jacarepaguá",
    228: "RJ - Gamboa",
    229: "Nit - Caio Martins",
    252: "Monitor - CO Plaza Shopping",
    281: "E. Móvel - Linha Amarela LAMSA - RJ",
    282: "E. Móvel - Lagoa - RJ.",
    291: "E. Móvel - Velha-Cidade Meninos",
    292: "E. Móvel - Resende",
    293: "E. Móvel - Parmalat Macae-RJ",
    294: "E. Móvel - Macaé - Norte Fuminense",
    295: "E. Móvel - Jardim Meriti - Vilar dos Teles - RJ OF",
    296: "E. Móvel - Itaguaí EMBRAPA",
    297: "E. Móvel - Engenheiro Pedreira",
    298: "E. Móvel - Belford Roxo",
    299: "E. Móvel - Barra Mansa",
    300: "E. Móvel - Velha - Petrópolis",
    609: "Itaborai - Ciep 130 - Meteorologia",
    610: "Itaborai - Vor Infraero - Meteorologia",
    611: "Radar Vor Da Infraero - Cetrel-Automatica",
    613: "Estação Meteorológica - Ute Campos",
    608: "Itb - Alto do Jacú",
    637: "VR - Nossa Sra. das Graças (Van)",
    730: "E. M. Francisco C. de Alvarenga",
    733: "DC - Bacia de Resfriamento",
    735: "DC - Campos Elíseos (Antiga)",
    737: "DC - Pier das Chatas",
    740: "Mc - Macaé Merchant",
    742: "RJ - Aeroporto de Campo dos Afonsos",
    743: "Mc - Aeroporto de Macaé",
    744: "RJ - Aeroporto do Galeão",
    745: "SC - Base Aérea de Santa Cruz",
    746: "SG - GETEC",
    747: "Itg - Estação Gaia",
    748: "Nit - Charitas",
    749: "Nit - Itaipu",
    750: "Mt - Terminal da Ilha Guaíba",  # 2013
    788: "Qmd - Meteorológica Jardim Riachão",
    789: "Pet - Retiro",
    804: "Itg - Brisamar",
    # =============================================== semiautomaticas ===============================================
    # --- Região da Costa Verde 
    201: "S - AR - Ilha Grande - UERJ",  #sem dado encontrado em 2025
    727: "S - Mt - Ilha Guaíba", #sem dado encontrado em 2025
    728: "S - Mt - Itacuruçá", #sem dado encontrado em 2025
    729: "S - Mt - Muriqui", #sem dado encontrado em 2025

    # --- Região das Baixadas Litorâneas  
    692: "S - Ara - Morro Grande",  #sem dado encontrado em 2025
    722: "S - Ara - SIGIL", #sem dado encontrado em 2025
    831: "S - CF - Tamoios 1", #new
    832: "S - CF - Tamoios 2", #new
    822: "S - SPA - Alecrim", #new
    233: "S - SPA - Campo Redondo 1",
    710: "S - SPA - Campo Redondo 2",

    # --- Região do Médio Paraíba  
    212: "S - BM - Ano Bom",
    709: "S - Itt - Rua Oito",  #sem dado encontrado em 2025
    708: "S - Itt - Rua Quarenta e Quatro",  #sem dado encontrado em 2025
    258: "S - Manual - Resende - Morada da Colina",  #sem dado encontrado em 2025
    257: "S - Manual - Volta Redonda - Belmonte",  #sem dado encontrado em 2025
    256: "S - Manual - Volta Redonda - C.Pesquisa",  #sem dado encontrado em 2025
    255: "S - Manual - Volta Redonda Banerj",  #sem dado encontrado em 2025
    254: "S - Manual - Volta Redonda J. Europa",  #sem dado encontrado em 2025
    802: "S - Pir - Caiçara",
    243: "S - Ponte Coberta",  #sem dado encontrado em 2025
    245: "S - Ribeirão das Lajes",  #sem dado encontrado em 2025
    154: "S - Rs - Pólo Industrial",
    116: "S - VR - Aeroclube",
    244: "S - VR - Água Limpa",  #sem dado encontrado em 2025
    650: "S - VR - Brasilândia",
    117: "S - VR - Centro", # verificado até aqui 26 jul 2026
    119: "S - VR - Conforto",
    238: "S - VR - Igreja de Santa Edwiges",
    148: "S - VR - Jardim Paraíba",
    120: "S - VR - Ponte Alta",
    651: "S - VR - São Luís",
    118: "S - VR - Vila Mury",
    146: "S - VR - Volta Grande",

    # Região Metropolitana
    667: "S - BR - Bom Pastor",
    211: "S - BR - Cedae",
    664: "S - BR - Malhapão",
    668: "S - BR - Nova Piam",
    669: "S - BR - Parque Martinho",
    276: "S - BR - Piam",
    666: "S - BR - Santa Maria",
    210: "S - BR - Secretaria de Transporte",
    734: "S - DC - Bacia de Resfriamento",
    204: "S - DC - Campos Elíseos",
    691: "S - DC - Comunidade",
    202: "S - DC - Jardim Primavera",
    203: "S - DC - Jardim Vinte e Cinco de Agosto",
    803: "S - DC - Parada Angélica",
    736: "S - DC - Pier das Chatas",
    738: "S - DC - Reservatório de Segurança",
    739: "S - DC - SETRE",
    741: "S - DC - Taquara",
    603: "S - Inoã - Lavador Da Pedreira",
    127: "S - Itb - Alto do Jacu",
    690: "S - Itb - Badureco",
    131: "S - Itb - Itambi",
    638: "S - Itb - Itambi (DNIT)",
    785: "S - Itb - Pachecos",
    827: "S - Itb - Pachecos 2", #new
    132: "S - Itb - Porto das Caixas",
    133: "S - Itb - Sambaetiba",
    129: "S - Itb - Sambaetiba (Fazenda Macacu)",
    130: "S - Itb - Vale das Pedrinhas",
    816: "S - Itg - Amendoeira",
    687: "S - Itg - Brisa Mar",
    689: "S - Itg - Centro",
    686: "S - Itg - Parque Paraíso",
    824: "S - Itg - Santana", #new    
    598: "S - Itg - Vila Ibirapitanga (Área interna)", #new nome
    815: "S - Itg - Vila Ibirapitanga",
    688: "S - Itg - Vila Margarida",
    234: "S - Jp - Vila Japeri",
    239: "S - Ma - Nova Luzitânia", #S - Ma - Inoã", new nome
    753: "S - Manual - Belford Roxo - Farrula",
    273: "S - Manual - Cascadura",
    272: "S - Manual - Centro Antiga",
    271: "S - Manual - Coelho Neto",
    270: "S - Manual - Copacabana - Light",
    269: "S - Manual - Duque de Caxias - Fórum",
    268: "S - Manual - Engenho da Rainha",
    267: "S - Manual - Ilha do Governador",
    266: "S - Manual - Ilha do Governador Antiga",
    265: "S - Manual - Inhaúma",
    264: "S - Manual - Maracanã  Antiga",
    263: "S - Manual - Méier Antiga 1",
    262: "S - Manual - Mesquita",
    261: "S - Manual - Nilópolis Antiga",
    260: "S - Manual - Nova Iguaçu Horto",
    259: "S - Manual - Queimados",
    232: "S - Mg - Bombeiros",
    685: "S - Mg - Convem Mineração",
    121: "S - Mg - Fazenda Caju",
    241: "S - Mg - Magé (DNIT)",
    823: "S - Mg - Santa Dalila", #new
    717: "S - Mg - Suruí",
    235: "S - Mg - Vila Inca",
    194: "S - NI - Centro",
    606: "S - NI - Cerâmica",
    805: "S - NI - Marapicu",
    599: "S - NI - Parque Rodilar",
    673: "S - Nit - AABB/Piratininga",
    675: "S - Nit - Águas de Niterói/Itaipu",
    191: "S - Nit - Centro",
    187: "S - Nit - Centro",
    676: "S - Nit - Corpo de Bombeiros/Itaipu",
    674: "S - Nit - DPO/Cafubá",
    677: "S - Nit - E M Francisco Portugal Neves/Piratininga",
    189: "S - Nit - Fonseca",
    678: "S - Nit - Hospital Psiquiatrico/Jurujuba",
    242: "S - Nit - Jurujuba",
    185: "S - Np - Rodoviária",
    719: "S - Pedreira Vigne Ltda.",
    820: "S - Pet - Bingen", #new
    801: "S - Prb - Dutra 103",
    236: "S - Qmd - Jardim Excelsior",
    724: "S - RJ - Alvorada",
    682: "S - RJ - Bandeirantes",
    173: "S - RJ - Bangu 1", #new name
    615: "S - RJ - Bangu 2", #new name
    705: "S - RJ - Barra da Tijuca",
    701: "S - RJ - Batalhão",
    184: "S - RJ - Benfica",
    679: "S - RJ - Bosque da Boiúna",
    181: "S - RJ - Botafogo",
    155: "S - RJ - Botafogo (Urca)",
    179: "S - RJ - Cajú",
    209: "S - RJ - Campo Grande",
    230: "S - RJ - Campos dos Afonsos",
    704: "S - RJ - Cantagalo",
    177: "S - RJ - Centro",
    176: "S - RJ - Cidade de Deus",
    175: "S - RJ - Copacabana",
    670: "S - RJ - Copacabana 2",
    681: "S - RJ - Curicica",
    172: "S - RJ - Engenho de Dentro",
    693: "S - RJ - Frente da Mineração",
    170: "S - RJ - Gamboa",
    702: "S - RJ - Gastão Baiana",
    707: "S - RJ - Gávea",
    828: "S - RJ - Gavea 1", #new
    829: "S - RJ - Gavea 2", #new
    144: "S - RJ - Ilha De Paquetá",
    712: "S - RJ - Inhaúma",
    139: "S - RJ - Inhaúma",
    780: "S - RJ - Inhaúma", #"S - RJ - Inhaúma (Polimix)",
    781: "S - RJ - Inhaúma (Concretan)",
    699: "S - RJ - Ipanema",
    683: "S - RJ - João Cribbin",
    725: "S - RJ - João XXIII A",
    726: "S - RJ - João XXIII B",
    167: "S - RJ - Lagoa",
    698: "S - RJ - Leblon",
    166: "S - RJ - Leblon",
    703: "S - RJ - Leopoldina",
    156: "S - RJ - Maracanã",
    165: "S - RJ - Maracanã",
    697: "S - RJ - Melo Duarte",
    731: "S - RJ - Palmares",
    700: "S - RJ - Pça. Jardim de Alah",
    182: "S - RJ - Ramos",
    164: "S - RJ - Ramos (Piscinão)",
    163: "S - RJ - Realengo",
    168: "S - RJ - Recreio dos Bandeirantes",
    160: "S - RJ - Rio Comprido",
    680: "S - RJ - Rio Grande",
    152: "S - RJ - Santa Cruz",
    153: "S - RJ - Santa Cruz (Conjunto Alvorada)",
    162: "S - RJ - Santa Tereza",
    706: "S - RJ - São Conrado",
    161: "S - RJ - São Cristovão",
    723: "S - RJ - Serra da Misericórdia - Inhaúma",
    247: "S - RJ - Taquara",
    158: "S - RJ - Tijuca",
    732: "S - RJ - Urucania",
    600: "S - RJ - Vargem Pequena",
    684: "S - RJ - Ventura",
    169: "S - RJ - Vila Militar",
    718: "S - SG - Área de Lavras",
    250: "S - SG - Colubandê",
    604: "S - SG - Engenho do Roçado",
    713: "S - SG - Estrada da Carioca",
    716: "S - SG - Lindo Parque", #"S - SG - Rua Major Januário",
    151: "S - SG - Prefeitura",
    821: "S - SG - Rocha", #new
    715: "S - SG - Rua Rio Juruá",
    614: "S - SG - Santa Isabel",
    150: "S - SJM - Vilar dos Teles",
    149: "S - Sp - Embrapa",
    602: "S - Sp - Fazenda Caxias 1",
    607: "S - Sp - Fazenda Caxias 2",
    248: "S - Sp - Nazaré",
    720: "S - Sp - Portaria Norte",
    721: "S - Sp - Portaria Sudeste",
    237: "S - Sp - Zona Rural",
    711: "S - Tan - Mineração Sartor",
    249: "S - Tan - Vila Cortes",

    # Região Noroeste Fluminense
    617: "S - Itp - Cubatão",
    672: "S - Itv - São Joaquim", #new

    # Região Norte Fluminense
    825: "S - CG - Ibitioca", # new
    826: "S - CM - Outeiro", #new
    208: "S - Cp - Águas do Paraíba",
    207: "S - Cp - Centro",
    206: "S - Cp - Goytacazes",
    205: "S - Cp - Rodoviária",
    663: "S - Mc - Boa Fé",
    671: "S - Mc - Cabiúnas",
    662: "S - Mc - Horto",
    696: "S - Mc - Imboassica",
    800: "S - Mc - Vila Iriri",
    #672: "S - São Joaquim",
    656: "S - SJB - Barra do Açu",
    694: "S - Sjb - Barra Do Açu 2",
    654: "S - SJB - Mato Escuro",
    655: "S - SJB - Mato Escuro (Centro)",
    652: "S - SJB - Pipeiras 1",
    695: "S - SJB - Pipeiras 2",
    657: "S - SJB - Porto do Açu",

    # Região Serrana
    137: "S - Cg - Ruínas",
    135: "S - Cg - Vila",
    752: "S - Manual - Cantagalo (Ruínas)",
    751: "S - Manual - Cantagalo (Vila)",
    246: "S - Ter - Vale Alpino",
}

df_stations = pd.DataFrame(list(stations_dict.items()), columns=["station_id", "station_name"])
df_stations= df_stations.drop_duplicates()

# Transformando em dataframe
df_parametros = pd.DataFrame(station_parameters_dict.items(), columns=["parameter_name", "parameter_id"])


#directory_path = '/home/nobre/Notebooks/RQAR_2025_book/data/DADOS_BRUTOS/RJ/RJ' 


file_sizes = []
filenames = []
for filename in os.listdir(directory_path):
    #print(filename)
    filepath = os.path.join(directory_path, filename)
    if os.path.isfile(filepath): # Check if it's a file, not a directory
        size_in_bytes = os.path.getsize(filepath)
        file_sizes.append(size_in_bytes)
        filenames.append(filename)
#print(file_sizes)
 
df_files = pd.DataFrame({'filenames':filenames})
df_files[['ANO','ESTACAO', 'PARAMETRO']] =  df_files['filenames'].str.split('_', expand=True)
df_files[['PARAMETRO', 'EXTENSAO']] = df_files['PARAMETRO'].str.split('.', expand=True)
df_files['TAMANHO'] = file_sizes
 
pn=[]
en=[]

# CORRIGIDO (5): alguns códigos de ESTACAO/PARAMETRO presentes nos nomes dos
# arquivos não existem em stations_dict/station_parameters_dict. Antes,
# estname.values[0] / parname.values[0] quebravam com IndexError quando a
# busca não encontrava nada. Agora tratamos esse caso: usamos um valor de
# fallback e avisamos no console quais códigos estão faltando, para que
# possam ser adicionados aos dicionários depois.
estacoes_faltantes = set()
parametros_faltantes = set()

for ii, row in df_files.iterrows():
    #print(row)
    parname = df_parametros['parameter_name'][row.PARAMETRO == df_parametros.parameter_id]
    if len(parname) == 0:
        parametros_faltantes.add(row.PARAMETRO)
        pn.append(f"DESCONHECIDO ({row.PARAMETRO})")
    else:
        pn.append(parname.values[0])
 
    estname = df_stations['station_name'][int(row.ESTACAO) == df_stations.station_id]
    if len(estname) == 0:
        estacoes_faltantes.add(row.ESTACAO)
        en.append(f"DESCONHECIDA ({row.ESTACAO})")
    else:
        en.append(estname.values[0])
    #print(parname)
 
if estacoes_faltantes:
    print(f"[AVISO] Códigos de ESTACAO não encontrados em stations_dict: {sorted(estacoes_faltantes)}")
if parametros_faltantes:
    print(f"[AVISO] Códigos de PARAMETRO não encontrados em station_parameters_dict: {sorted(parametros_faltantes)}")
 
df_files['PARNAME'] = pn
df_files['ESTNAME'] = en
 
df_files = df_files[df_files['TAMANHO']>1]
 
# Sort by 'Age' in ascending order
df_files = df_files.sort_values(by='ANO')
 
df_files_years = df_files.groupby(['ESTACAO','ESTNAME', 'PARAMETRO','PARNAME']).agg({
    'ANO': lambda x: ', '.join(x),
    #'PARNAME': lambda Y: ', '.join(Y),
 
}).reset_index()
 
df_files_years['INICIO'] = np.nan
df_files_years['FIM'] = np.nan
df_files_years['NANOS'] = np.nan
df_files_years['NGAPS'] = np.nan
 
for ii, row in df_files_years.iterrows():
    
    df_files_years.loc[ii, "INICIO"]  = np.array(row['ANO'].split(','),dtype=int).min().item()
    df_files_years.loc[ii, "FIM"]  = np.array(row['ANO'].split(','),dtype=int).max().item()
    df_files_years.loc[ii, "NANOS"]  = np.array(row['ANO'].split(','),dtype=int).shape[0]
    
    if df_files_years.loc[ii, "INICIO"]==df_files_years.loc[ii, "FIM"]:
         df_files_years.loc[ii, "NGAPS"] =  0
    else:
        df_files_years.loc[ii, "NGAPS"] =  np.size(np.arange(df_files_years.loc[ii, "INICIO"],df_files_years.loc[ii, "FIM"]+1, 1)) - df_files_years.loc[ii,'NANOS']
 
df_files_years['INICIO'] = df_files_years['INICIO'].astype(int)
df_files_years['FIM'] = df_files_years['FIM'].astype(int)
df_files_years['NANOS'] = df_files_years['NANOS'].astype(int)
df_files_years['NGAPS'] = df_files_years['NGAPS'].astype(int)
 
# min_values_per_category = df_files.groupby(['ESTNAME','PARNAME'])['ANO'].min()
 
# df_files_years['INICIO'] = min_values_per_category.reset_index().ANO.astype(int)
 
# max_values_per_category = df_files.groupby(['ESTNAME','PARNAME'])['ANO'].max()
 
# df_files_years['FIM'] = max_values_per_category.reset_index().ANO.astype(int)
 
# count_years = df_files.groupby(['ESTNAME','PARNAME'])['ANO'].count()
 
# df_files_years['NANOS'] = count_years.reset_index().ANO
 
# df_files_years['NGAPS'] =  df_files_years.apply(lambda row: np.size(np.arange(row['INICIO'], row['FIM']+1, 1)), axis=1) - df_files_years['NANOS']
 
 
 
df_files_years.to_csv('/home/nobre/Notebooks/RQAr/dados/RJ_STATIONS_ANOS.csv', index=False)
#df_files.to_csv('/home/nobre/Notebooks/RQAR_2025_book/data/RJ_STATIONS.csv', index=False)
 
import pathlib

# year = 2025
# category = auto #manual
# directory_path = f'/home/nobre/Notebooks/RQAr/dados/dados_brutos/{year}/RJ/dados_coletados/{category}/'
# directory_out = f'/home/nobre/Notebooks/RQAr/dados/dados_formatados/{year}/monitoramento/RJ/'

mapping = {
    "3": "007",
    "7": "011",
    "9": "018",
    "11": "016",
    "18": "001",
    "20": "002",
    "23": "003",
    "134": "010",
    "263": "013",
    "413": "025",
    "482": "022",
    "504": "023",
    "1305": "014",
    "1465": "004",
    "1955": "008",
    "2128": "017",
    "2130": "005",
    "2143": "026",
    "2168": "027"
}

units = {
    "007": "ppm",
    "011": "ppm",
    "018": "µg/m³",
    "016": "ppm",
    "001": "µg/m³",
    "002": "µg/m³",
    "003": "µg/m³",
    "010": "µg/m³",
    "013": "µg/m³",
    "025": "µg/m³",
    "022": "µg/m³",
    "023": "µg/m³",
    "014": "µg/m³",
    "004": "µg/m³",
    "008": "µg/m³",
    "017": "µg/m³",
    "005": "µg/m³",
    "026": "ppm",
    "027": "µg/m³"
}

table_pols = pd.read_csv('/home/nobre/Notebooks/RQAr/dicionarios/CODIGO_POLUENTES.csv')

unique_df = df_files_years.drop_duplicates(subset=['ESTACAO', 'PARAMETRO']).copy()
print(len(df_files_years['ESTACAO'].unique()))
unique_df["nosso_parametro"] = unique_df["PARAMETRO"].map(mapping)
 
for ii, row in unique_df.iterrows():
    #print(str(row['ESTACAO'])+'_'+str(row['PARAMETRO']))
    df_list=[]
    all_files = glob.glob(directory_path + '*'+str(row['ESTACAO'])+'_'+str(row['PARAMETRO'])+'.csv')
 
    for lf in all_files:
        filepath = os.path.join(directory_path, lf)
        try:
            df = pd.read_csv(filepath)
        except Exception:
            df = pd.DataFrame()
            
        df_list.append(df)
    
    # CORRIGIDO (2): antes, se all_files vinha vazio, o loop acima nunca criava 'df'
    # e 'combined_df = df.copy()' lançava NameError. Agora tratamos explicitamente
    # o caso de 0 arquivos (pula com aviso) e usamos df_list[0] em vez de 'df' solto
    # para o caso de exatamente 1 arquivo.
    if len(all_files) == 0:
        print(f"[AVISO] Nenhum arquivo encontrado para ESTACAO={row['ESTACAO']} "
              f"PARAMETRO={row['PARAMETRO']} em {directory_path}. Pulando.")
        continue
    elif len(all_files) > 1:
        combined_df = pd.concat(df_list, ignore_index=True)
    else:
        combined_df = df_list[0]
 
    combined_df.rename(columns={'datetime': 'DATETIME'}, inplace=True)
    # CORRIGIDO (4): usa parse_datetime_misto para lidar com meses abreviados em
    # português (ex: '01-fev-2025 00:00'), que causavam DateParseError.
    combined_df['DATETIME'] = parse_datetime_misto(combined_df['DATETIME'])
    combined_df['ANO'] = pd.to_datetime(combined_df['DATETIME']).dt.year
    combined_df['MES'] = pd.to_datetime(combined_df['DATETIME']).dt.month
    combined_df['DIA'] = pd.to_datetime(combined_df['DATETIME']).dt.day
    combined_df['HORA'] = pd.to_datetime(combined_df['DATETIME']).dt.hour
    combined_df = combined_df.rename(columns={'value':'VALOR','qaqc':'QAQC_INTERNO'})
    
    combined_df = combined_df.drop_duplicates()
    combined_df = combined_df.sort_values(by='DATETIME')
    combined_df = tratar_dados(combined_df)
    
    #combined_df
    #combined_df['value'].plot()
    if isinstance(row['nosso_parametro'], str):
        combined_df['UNIDADE'] = units[row['nosso_parametro']]
        name_file = table_pols.loc[table_pols['COD_POLUENTE'] == int(row['nosso_parametro']), 'NOME_PASTA'].values[0]
        # CORRIGIDO (3): os.path.join no lugar de concatenação com '+', e criação da pasta
        # de destino caso ainda não exista.
        out_path = os.path.join(
            directory_out, name_file,
            f"RJ{str(row['ESTACAO']).zfill(4)}RA{str(row['nosso_parametro']).zfill(3)}.csv"
        )
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        combined_df.to_csv(out_path, index=False)
    else:
        # CORRIGIDO (3): idem, para a pasta METEOROLOGICO.
        out_path = os.path.join(
            directory_out, 'METEOROLOGICO',
            f"RJ{str(row['ESTACAO']).zfill(4)}MA{str(row['PARAMETRO']).zfill(3)}.csv"
        )
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        combined_df.to_csv(out_path, index=False)
 
