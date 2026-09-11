import pandas as pd


def padroniza_coluna_datetime(caminho_arquivo):
    """
    Renomeia a primeira coluna do arquivo para DATETIME.

    A função não altera os valores da coluna nem as demais colunas.
    """

    # Lê o arquivo
    df = pd.read_csv(
        caminho_arquivo,
        dtype=str
    )

    # Guarda o nome atual da primeira coluna
    nome_coluna_atual = df.columns[0]

    # Renomeia a primeira coluna
    df = df.rename(
        columns={
            nome_coluna_atual: "DATETIME"
        }
    )

    # Sobrescreve o próprio arquivo
    df.to_csv(
        caminho_arquivo,
        index=False,
        encoding="utf-8",
        sep=","
    )

    print(
        f"Primeira coluna '{nome_coluna_atual}' "
        f"padronizada para 'DATETIME'."
    )