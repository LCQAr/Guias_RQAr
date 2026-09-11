from pathlib import Path
import pandas as pd
def padronizar_colunas(
    UF,
    ano,
    pasta_rede="/home/nobre/Notebooks/RQAr/dados/dados_formatados",
):
    """
    Padroniza a estrutura das colunas da planilha da rede de monitoramento.

    O arquivo da rede de monitoramento é localizado automaticamente
    a partir da UF e do ano informados.

    A função:
    - Monta automaticamente o caminho do arquivo UF_Rede_ANO.csv;
    - Corrige nomes de colunas conhecidos;
    - Renomeia as colunas para o padrão do projeto;
    - Cria as colunas obrigatórias ausentes;
    - Organiza as colunas na ordem padrão;
    - Salva novamente o arquivo.

    Parâmetros
    ----------
    UF : str
        Sigla da Unidade Federativa correspondente ao arquivo.

    ano : int
        Ano correspondente ao arquivo da rede de monitoramento.

    pasta_rede : str, opcional
        Caminho da pasta principal onde estão os arquivos formatados.
        O ano e a pasta "rede" são adicionados automaticamente.

        Padrão:
        "/home/nobre/Notebooks/RQAr/dados/dados_formatados"

    Retorna
    -------
    df : pandas.DataFrame
        DataFrame com a estrutura das colunas padronizada.

    Exemplo
    -------
    padronizar_colunas("RJ", 2024)

    O arquivo utilizado será:
        /home/nobre/Notebooks/RQAr/dados/dados_formatados/2024/rede/RJ_Rede_2024.csv
    """

    # ==========================================================
    # CAMINHO
    # ==========================================================

    caminho = (
        Path(pasta_rede)
        / str(ano)
        / "rede"
        / f"{UF.upper()}_Rede_{ano}.csv"
    )

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado:\n{caminho}"
        )

    # ==========================================================
    # LEITURA
    # ==========================================================

    df = pd.read_csv(
        caminho,
        dtype=str
    )

    # ==========================================================
    # MAPA DE COLUNAS
    # ==========================================================

    mapa_colunas = {
        "Cidade": "CIDADE",
        "Proprietário da estação": "PROPRIETARIO",
        "Tipo de entidade do proprietário (pública ou privada)": "PROP_ENTIDADE",
        "Entidade responsável por operar a estação": "OPERADOR",
        "Tipo de entidade do operador (pública ou privada)": "OP_ENTIDADE",
        "Princípio de funcionamento": "FUNCIONAMENTO",
        "Tipo da estação": "CATEGORIA",
        "Princípio de medição": "METODO",
        "Frequência de calibração": "CALIBRACAO",
        "Marca do equipamento": "MARCA",
        "Modelo do equipamento": "MODELO",
        "Poluentes monitorados": "POLUENTE",
        "Estação fixa ou móvel?": "MOBILIDADE",
        "Representação espacial": "REP_ESPACIAL",
        "Finalidade de monitoramento": "FINALIDADE",
        "Status de operação ": "STATUS",
        "Data de início da operação": "INICIO",
        "Data de fim da operação": "FIM",
        "Latitude": "LATITUDE",
        "Longitude": "LONGITUDE",
        "Integrada no MonitorAr?": "MONITORAR",
        "A estação foi realocada no último ano?": "REALOCACAO",
        "Observações sobre a agenda de calibração": "OBS_CALIBRACAO",
        "Observações gerais sobre a estação de monitoramento": "OBS_GERAIS"
    }

    # ==========================================================
    # CORRIGE ERRO DE DIGITAÇÃO CONHECIDO
    # ==========================================================

    if "Prooprietário da estação" in df.columns:
        df = df.rename(
            columns={
                "Prooprietário da estação":
                "Proprietário da estação"
            }
        )

    # ==========================================================
    # RENOMEIA APENAS AS COLUNAS EXISTENTES
    # ==========================================================

    df = df.rename(
        columns={
            k: v
            for k, v in mapa_colunas.items()
            if k in df.columns
        }
    )

    # ==========================================================
    # ESTRUTURA PADRÃO
    # ==========================================================

    estrutura = [
        "UF",
        "CIDADE",
        "CD_MUN",
        "ID_OEMA_ORIGINAL",
        "ID_OEMA",
        "ID_MMA",
        "ID_MMA_COMPLETO",
        "PROPRIETARIO",
        "PROP_ENTIDADE",
        "OPERADOR",
        "OP_ENTIDADE",
        "FUNCIONAMENTO",
        "CATEGORIA",
        "METODO",
        "CALIBRACAO",
        "MARCA",
        "MODELO",
        "POLUENTE",
        "COD_POLUENTE",
        "MOBILIDADE",
        "REP_ESPACIAL",
        "FINALIDADE",
        "STATUS",
        "INICIO",
        "FIM",
        "LATITUDE",
        "LONGITUDE",
        "MONITORAR",
        "FONTE",
        "CERTIFICACAO",
        "COD_UF_IBGE",
        "ANOS_MONITORADOS",
        "BASE_DADOS",
        "ELEVACAO",
        "REALOCACAO",
        "OBS_CALIBRACAO",
        "DADOS_MONITORAMENTO",
        "RECONHECIDA",
        "OBS_GERAIS",
        "REP_ESPACIAL_DECLARADA",
        "OPERACAO"
    ]

    # ==========================================================
    # CRIA COLUNAS AUSENTES
    # ==========================================================

    for coluna in estrutura:

        if coluna not in df.columns:
            df[coluna] = pd.NA

    # ==========================================================
    # ORGANIZA A ORDEM
    # ==========================================================

    df = df[estrutura]

    # ==========================================================
    # SALVA
    # ==========================================================

    df.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"✅ Estrutura padronizada com sucesso!"
    )

    print(
        f"Arquivo salvo em:\n{caminho}"
    )

    return df