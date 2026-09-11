import re
import unicodedata
from pathlib import Path
import pandas as pd

def padroniza_ID_OEMA(
    caminho_arquivo,
    coluna="ID_OEMA",
    UF=None,
    ano=None,
    pasta_saida="/home/nobre/Notebooks/RQAr/dados/dados_formatados",
):
    """
    Padroniza a coluna ID_OEMA e salva o arquivo formatado.

    Parâmetros
    ----------
    caminho_arquivo : str
        Caminho do arquivo CSV de entrada.

    coluna : str
        Nome da coluna original da estação.
        Padrão: "ID_OEMA".

    UF : str
        Sigla da UF utilizada no nome do arquivo de saída.

    ano : int
        Ano utilizado no caminho e nome do arquivo de saída.

    pasta_saida : str
        Pasta base dos arquivos formatados.

    Retorna
    -------
    df : pandas.DataFrame
        DataFrame com ID_OEMA_ORIGINAL e ID_OEMA padronizados.
    """

    # Lê o arquivo
    df = pd.read_csv(caminho_arquivo, dtype=str)

    if coluna not in df.columns:
        raise ValueError(
            f"A coluna '{coluna}' não existe no arquivo."
        )

    # Guarda o nome original
    df = df.rename(
        columns={coluna: "ID_OEMA_ORIGINAL"}
    )

    # Padroniza o nome
    def padronizar(texto):

        if pd.isna(texto):
            return texto

        texto = unicodedata.normalize(
            "NFKD", str(texto).lower()
        ).encode(
            "ASCII", "ignore"
        ).decode()

        texto = re.sub(
            r"[\s,-]+", "_", texto
        )

        texto = re.sub(
            r"[^a-z0-9_]", "", texto
        )

        return re.sub(
            r"_+", "_", texto
        ).strip("_")

    # Cria ID_OEMA padronizado
    df["ID_OEMA"] = df[
        "ID_OEMA_ORIGINAL"
    ].apply(padronizar)

    # Coloca ID_OEMA ao lado do original
    colunas = list(df.columns)
    colunas.remove("ID_OEMA")

    posicao = colunas.index(
        "ID_OEMA_ORIGINAL"
    ) + 1

    colunas.insert(
        posicao,
        "ID_OEMA"
    )

    df = df[colunas]

    # Salva
    if UF is not None and ano is not None:

        caminho_saida = (
            Path(pasta_saida)
            / str(ano)
            / "rede"
        )

        caminho_saida.mkdir(
            parents=True,
            exist_ok=True
        )

        arquivo_saida = (
            caminho_saida
            / f"{UF.upper()}_Rede_{ano}.csv"
        )

        df.to_csv(
            arquivo_saida,
            index=False,
            encoding="utf-8"
        )

        print(
            f"Arquivo salvo em:\n{arquivo_saida}"
        )

    return df