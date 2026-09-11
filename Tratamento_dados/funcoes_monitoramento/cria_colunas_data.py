import pandas as pd


def cria_colunas_data(caminho_arquivo):
    """
    A função tem como objeitvo criar as colunas ANO, DIA, MES, HORA com base no DATAFRAME padronizado pela leitura do Pandas
    """

    # Lê o CSV
    df = pd.read_csv(caminho_arquivo)

    # Garante que DATETIME seja datetime
    df["DATETIME"] = pd.to_datetime(
        df["DATETIME"],
        errors="coerce"
    )

    # Cria ANO
    df.insert(
        1,
        "ANO",
        df["DATETIME"].dt.year
    )

    # Cria MES
    df.insert(
        2,
        "MES",
        df["DATETIME"].dt.month
    )

    # Cria DIA
    df.insert(
        3,
        "DIA",
        df["DATETIME"].dt.day
    )

    # Cria HORA
    df.insert(
        4,
        "HORA",
        df["DATETIME"].dt.hour
    )

    # Salva
    df.to_csv(
        caminho_arquivo,
        index=False,
        encoding="utf-8",
        sep=","
    )

    print(
        "Colunas ANO, MES, DIA e HORA "
        "criadas com sucesso!"
    )