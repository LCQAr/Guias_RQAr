import pandas as pd


def aplica_booleano_qaqc(caminho_arquivo):

    # Caminho do dicionário
    caminho_dicionario = (
        "/home/nobre/Notebooks/RQAr/dicionarios/"
        "dicionario_flags.csv"
    )

    # Lê o arquivo
    df = pd.read_csv(
        caminho_arquivo,
        dtype=str
    )

    # Lê o dicionário
    dicionario = pd.read_csv(
        caminho_dicionario,
        dtype=str
    )

    # Normaliza as flags do dicionário
    dicionario["FLAG_QAQC_INTERNO"] = (
        dicionario["FLAG_QAQC_INTERNO"]
        .fillna("")
        .str.strip()
    )

    # Converte TRUE/FALSE do dicionário para booleano
    dicionario["VALIDO"] = (
        dicionario["VALIDO"]
        .fillna("")
        .str.strip()
        .str.upper()
        .map({
            "TRUE": True,
            "FALSE": False
        })
    )

    # Cria o mapa FLAG -> BOOLEANO
    mapa_flags = dict(
        zip(
            dicionario["FLAG_QAQC_INTERNO"],
            dicionario["VALIDO"]
        )
    )

    # Identifica as colunas QAQC
    colunas_qaqc = [
        coluna for coluna in df.columns
        if coluna.startswith("QAQC_")
    ]

    # Aplica o booleano em cada coluna QAQC
    for coluna in colunas_qaqc:

        # Guarda os valores originais
        valores_originais = df[coluna].copy()

        # Normaliza somente para fazer a comparação
        valores_normalizados = (
            df[coluna]
            .fillna("")
            .str.strip()
        )

        # Faz a conversão para True/False
        valores_booleanos = valores_normalizados.map(mapa_flags)

        # Verifica flags desconhecidas
        desconhecidos = valores_normalizados[
            valores_booleanos.isna() &
            valores_normalizados.ne("")
        ].unique()

        if len(desconhecidos) > 0:
            raise ValueError(
                f"A coluna {coluna} possui flags que não estão "
                f"no dicionário: {list(desconhecidos)}"
            )

        # Substitui pela informação booleana
        df[coluna] = valores_booleanos.astype("boolean")

    # Sobrescreve o arquivo original
    df.to_csv(
        caminho_arquivo,
        index=False,
        encoding="utf-8",
        sep=","
    )
