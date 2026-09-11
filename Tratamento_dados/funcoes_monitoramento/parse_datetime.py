import pandas as pd


def parse_datetime(x):
    """
    Tenta interpretar diferentes formatos de DATETIME
    encontrados nos arquivos e retorna um datetime
    compatível com o pandas.
    """

    if pd.isna(x):
        return pd.NaT

    x = str(x).strip()

    if x == "":
        return pd.NaT

    formatos = [
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%m/%d/%Y %I:%M:%S %p"
    ]

    for formato in formatos:

        try:

            return pd.to_datetime(
                x,
                format=formato
            )

        except (ValueError, TypeError):

            continue

    # Última tentativa para formatos não previstos
    return pd.to_datetime(
        x,
        errors="coerce"
    )