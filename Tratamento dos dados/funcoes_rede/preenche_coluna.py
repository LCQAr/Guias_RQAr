from pathlib import Path
import pandas as pd


def preencher_coluna(uf, coluna, valor):
    """
    Preenche todos os registros de uma coluna de um arquivo CSV
    com um valor.

    O arquivo da rede de monitoramento é localizado automaticamente
    a partir da UF informada.

    Parâmetros
    ----------
    uf : str
        Sigla da Unidade Federativa (UF) correspondente ao arquivo
        da rede de monitoramento.

    coluna : str
        Nome da coluna que será preenchida.

    valor : qualquer tipo
        Valor que será atribuído a todos os registros da coluna.

    Retorna
    -------
    df : pandas.DataFrame
        DataFrame com a coluna preenchida.

    caminho_csv : pathlib.Path
        Caminho do arquivo CSV atualizado.

    Exemplo
    -------
    preencher_coluna("RJ", "UF", "RJ")

    O arquivo utilizado será:
        /home/nobre/Notebooks/RQAr/dados/dados_formatados/2025/rede/RJ_Rede_2025.csv
    """

    # ==========================================================
    # CAMINHO DO ARQUIVO
    # ==========================================================

    pasta_rede = Path(
        "/home/nobre/Notebooks/RQAr/"
        "dados/dados_formatados/2025/rede"
    )

    caminho_csv = (
        pasta_rede / f"{uf.upper()}_Rede_2025.csv"
    )

    # ==========================================================
    # LÊ O ARQUIVO
    # ==========================================================

    df = pd.read_csv(
        caminho_csv,
        dtype=str
    )

    # ==========================================================
    # VERIFICA SE A COLUNA EXISTE
    # ==========================================================

    if coluna not in df.columns:
        raise ValueError(
            f"A coluna '{coluna}' não existe no arquivo."
        )

    # ==========================================================
    # PREENCHE A COLUNA
    # ==========================================================

    df[coluna] = valor

    # ==========================================================
    # SALVA O ARQUIVO
    # ==========================================================

    df.to_csv(
        caminho_csv,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"✅ Coluna '{coluna}' preenchida com '{valor}'."
    )

    print(
        f"Arquivo atualizado:\n{caminho_csv}"
    )

    return df, caminho_csv