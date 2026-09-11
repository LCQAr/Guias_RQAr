from pathlib import Path
import pandas as pd
import chardet
def padroniza_arquivos(caminho_arquivo, skiprows=0):
    """
    Converte arquivos (.xlsx, .xls, .csv ou .txt) para CSV
    utilizando UTF-8 e separador ','.

    Parâmetros
    ----------
    caminho_arquivo : str ou Path
        Caminho do arquivo de entrada.

    skiprows : int, opcional
        Número de linhas a ignorar na leitura (útil para Excel).

    Retorna
    -------
    df : pandas.DataFrame
        DataFrame lido.

    arquivo_csv : pathlib.Path
        Caminho do CSV gerado.
    """

    caminho_arquivo = Path(caminho_arquivo)
    extensao = caminho_arquivo.suffix.lower()

    # ===========================
    # Arquivos Excel
    # ===========================
    if extensao in [".xlsx", ".xls"]:

        df = pd.read_excel(
            caminho_arquivo,
            skiprows=skiprows
        )

    # ===========================
    # Arquivos CSV ou TXT
    # ===========================
    elif extensao in [".csv", ".txt"]:

        # Detecta o encoding
        with open(caminho_arquivo, "rb") as f:
            encoding = chardet.detect(f.read())["encoding"]

        # Lê automaticamente o separador
        df = pd.read_csv(
            caminho_arquivo,
            encoding=encoding,
            sep=None,
            engine="python"
        )

    else:
        raise ValueError(f"Formato '{extensao}' não suportado.")

    # Nome do CSV
    arquivo_csv = caminho_arquivo.with_suffix(".csv")

    # Salva padronizado
    df.to_csv(
        arquivo_csv,
        index=False,
        encoding="utf-8",
        sep=","
    )

    print(f"Arquivo convertido com sucesso!")
    print(f"CSV salvo em:\n{arquivo_csv}")

    return df, arquivo_csv