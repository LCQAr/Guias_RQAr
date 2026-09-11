import pandas as pd

from funcoes_monitoramento.parse_valor import parse_valor


def padroniza_valores(caminho_arquivo):
    """
    Padroniza os valores numéricos do arquivo.

    A função:

    - Ignora DATETIME, ANO, MES, DIA e HORA;
    - Ignora todas as colunas de UNIDADE;
    - Ignora todas as colunas de QAQC;
    - Aplica parse_valor somente nas colunas de valores;
    - Identifica e informa exatamente onde ocorreram erros;
    - Funciona tanto para arquivos com QAQC quanto sem QAQC.
    """

    # ==========================================================
    # 1. LÊ O ARQUIVO
    # ==========================================================

    df = pd.read_csv(
        caminho_arquivo,
        header=None,
        dtype=str
    )

    # ==========================================================
    # 2. IDENTIFICA AS COLUNAS DE VALOR
    # ==========================================================

    colunas_valor = []

    for col in df.columns:

        nome_coluna = str(
            df.iloc[0, col]
        ).strip()

        nome_maiusculo = nome_coluna.upper()

        # Ignora colunas de data/hora
        if nome_maiusculo in [
            "DATETIME",
            "ANO",
            "MES",
            "DIA",
            "HORA"
        ]:
            continue

        # Ignora colunas de unidade
        if nome_maiusculo.startswith("UNIDADE"):
            continue

        # Ignora todas as colunas de QAQC
        if nome_maiusculo.startswith("QAQC"):
            continue

        # O que sobrou é considerado coluna de valor
        colunas_valor.append(col)

    print(
        f"Colunas de valores encontradas: "
        f"{len(colunas_valor)}"
    )

    # ==========================================================
    # 3. PADRONIZA OS VALORES
    # ==========================================================

    erros = []

    for col in colunas_valor:

        nome_coluna = str(
            df.iloc[0, col]
        ).strip()

        for indice in range(3, len(df)):

            valor_original = df.iloc[indice, col]

            # Ignora valores vazios
            if pd.isna(valor_original):
                continue

            if str(valor_original).strip() == "":
                continue

            try:

                valor_padronizado = parse_valor(
                    valor_original
                )

                df.iloc[indice, col] = (
                    valor_padronizado
                )

            except (ValueError, TypeError) as erro:

                erros.append({
                    "coluna": nome_coluna,
                    "linha": indice + 1,
                    "valor": valor_original,
                    "erro": str(erro)
                })

    # ==========================================================
    # 4. SALVA O ARQUIVO
    # ==========================================================

    df.to_csv(
        caminho_arquivo,
        index=False,
        header=False,
        encoding="utf-8",
        sep=","
    )

    # ==========================================================
    # 5. RESULTADO
    # ==========================================================

    if len(erros) == 0:

        print(
            "✓ Valores padronizados sem erros."
        )

    else:

        print(
            f"\nATENÇÃO: foram encontrados "
            f"{len(erros)} erro(s)."
        )

        print(
            "\nLocalização dos erros:"
        )

        for erro in erros:

            print(
                f"  • Coluna: {erro['coluna']} | "
                f"Linha: {erro['linha']} | "
                f"Valor: {erro['valor']} | "
                f"Erro: {erro['erro']}"
            )

    print(
        f"\nArquivo atualizado em:\n"
        f"{caminho_arquivo}"
    )