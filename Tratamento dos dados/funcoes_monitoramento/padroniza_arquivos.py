from pathlib import Path
import pandas as pd
import chardet

def padroniza_arquivos(caminho, skiprows=0):
    """
    Converte um arquivo ou todos os arquivos de uma pasta para CSV,
    usando UTF-8 e separador ','.

    Se o caminho for um arquivo:
        Converte somente o arquivo informado.

    Se o caminho for uma pasta:
        Converte todos os arquivos .xlsx, .xls, .csv e .txt
        encontrados diretamente dentro da pasta.

    Os arquivos são salvos no mesmo local, mantendo o mesmo nome
    e alterando apenas a extensão para .csv.

    Parâmetros
    ----------
    caminho : str ou Path
        Caminho do arquivo ou da pasta.

    skiprows : int, opcional
        Número de linhas a ignorar na leitura de arquivos Excel.

    Retorna
    -------
    resultados : list
        Lista de tuplas contendo (DataFrame, caminho_csv).
    """

    caminho = Path(caminho)
    extensoes_suportadas = [".xlsx", ".xls", ".csv", ".txt"]

    if not caminho.exists():
        raise FileNotFoundError(f"O caminho não existe:\n{caminho}")

    if caminho.is_file():
        arquivos = [caminho]

    elif caminho.is_dir():
        arquivos = [
            arquivo
            for arquivo in caminho.iterdir()
            if arquivo.is_file()
            and arquivo.suffix.lower() in extensoes_suportadas
        ]

    else:
        raise ValueError(f"O caminho informado não é válido:\n{caminho}")

    resultados = []

    for arquivo in arquivos:
        extensao = arquivo.suffix.lower()

        if extensao in [".xlsx", ".xls"]:
            df = pd.read_excel(
                arquivo,
                skiprows=skiprows
            )

        elif extensao in [".csv", ".txt"]:
            with open(arquivo, "rb") as f:
                encoding = chardet.detect(f.read())["encoding"]

            if encoding is None:
                encoding = "utf-8"

            df = pd.read_csv(
                arquivo,
                encoding=encoding,
                sep=None,
                engine="python"
            )

        else:
            continue

        arquivo_csv = arquivo.with_suffix(".csv")

        df.to_csv(
            arquivo_csv,
            index=False,
            encoding="utf-8",
            sep=","
        )

        print(f"Convertido: {arquivo.name}")
        print(f"Salvo em:   {arquivo_csv}")

        resultados.append((df, arquivo_csv))

    if not resultados:
        print("Nenhum arquivo compatível encontrado.")

    return resultados
