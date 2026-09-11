import pandas as pd


def verifica_datetime(caminho_arquivo):
    """
    A função corrige a leitura para datetime do pandas
    """
    # Lê o CSV
    df = pd.read_csv(caminho_arquivo)

    # Tenta interpretar DATETIME como datetime
    datetime = pd.to_datetime(
        df["DATETIME"],
        errors="coerce",
        dayfirst=True
    )

    # Verifica se algum valor não pôde ser convertido
    if datetime.isna().any():

        quantidade_invalidos = datetime.isna().sum()

        print(
            f"Atenção: {quantidade_invalidos} "
            "registros não puderam ser interpretados como datetime."
        )

    else:

        print(
            "Todos os registros de DATETIME "
            "podem ser interpretados pelo pandas."
        )

    # Mostra o tipo resultante
    print(f"Tipo após leitura pelo pandas: {datetime.dtype}")