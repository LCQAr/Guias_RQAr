import pandas as pd

from funcoes_monitoramento.parse_datetime import (
    parse_datetime
)


def padroniza_datetime(caminho_arquivo):
    """
    Padroniza a coluna DATETIME de um arquivo.

    A função:
    - lê o arquivo;
    - interpreta cada valor utilizando parse_datetime();
    - transforma DATETIME para o padrão datetime do pandas;
    - verifica se existem valores que realmente não puderam
      ser interpretados;
    - salva o arquivo mantendo as demais colunas.
    """

    # ==========================================================
    # 1. LÊ O ARQUIVO
    # ==========================================================

    df = pd.read_csv(
        caminho_arquivo,
        dtype=str
    )

    # ==========================================================
    # 2. VERIFICA SE DATETIME EXISTE
    # ==========================================================

    if "DATETIME" not in df.columns:

        raise ValueError(
            "A coluna 'DATETIME' não existe no arquivo."
        )

    # ==========================================================
    # 3. GUARDA OS VALORES ORIGINAIS
    # ==========================================================

    datetime_original = df["DATETIME"].copy()

    # ==========================================================
    # 4. PADRONIZA CADA REGISTRO
    # ==========================================================

    df["DATETIME"] = (
        df["DATETIME"]
        .apply(parse_datetime)
    )

    # ==========================================================
    # 5. VERIFICA VALORES REALMENTE INVÁLIDOS
    # ==========================================================

    registros_invalidos = (
        df["DATETIME"].isna()
        & datetime_original.notna()
        & (
            datetime_original
            .astype(str)
            .str.strip()
            != ""
        )
    )

    quantidade_invalidos = (
        registros_invalidos.sum()
    )

    # ==========================================================
    # 6. MOSTRA O RESULTADO
    # ==========================================================

    if quantidade_invalidos == 0:

        print(
            "✓ DATETIME padronizado com sucesso."
        )

    else:

        print(
            f"Atenção: {quantidade_invalidos} "
            "registro(s) não puderam ser interpretados."
        )

        print(
            "\nValores que realmente apresentaram problema:"
        )

        valores_problematicos = (
            datetime_original[registros_invalidos]
            .drop_duplicates()
            .head(20)
        )

        for valor in valores_problematicos:

            print(
                f"  • {valor}"
            )

        raise ValueError(
            "Existem valores de DATETIME que não puderam "
            "ser interpretados."
        )

    # ==========================================================
    # 7. GARANTE O TIPO DATETIME DO PANDAS
    # ==========================================================

    if not pd.api.types.is_datetime64_any_dtype(
        df["DATETIME"]
    ):

        raise TypeError(
            "A coluna DATETIME não foi convertida "
            "para um tipo datetime do pandas."
        )

    print(
        f"Tipo da coluna DATETIME: "
        f"{df['DATETIME'].dtype}"
    )

    # ==========================================================
    # 8. SALVA O ARQUIVO
    # ==========================================================

    df.to_csv(
        caminho_arquivo,
        index=False,
        encoding="utf-8",
        sep=","
    )

    print(
        f"Arquivo atualizado em:\n"
        f"{caminho_arquivo}"
    )
