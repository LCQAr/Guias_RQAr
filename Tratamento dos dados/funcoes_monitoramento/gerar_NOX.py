import pandas as pd


def gerar_NOX(caminho_arquivo):

    """
    Cria ou atualiza as colunas de NOX a partir das medições
    de NO e NO2.

    A função identifica automaticamente os códigos de NO, NO2
    e NOX através do dicionário CODIGO_POLUENTES.

    Para cada estação:

    - utiliza os 6 primeiros caracteres do ID_MMA_COMPLETO
      como identificador da estação;
    - procura NO, NO2 e NOX pertencentes à mesma estação;
    - se NOX já existir, atualiza seus valores;
    - se NOX não existir, cria a coluna;
    - verifica se NO e NO2 possuem a mesma unidade;
    - verifica os DATETIME correspondentes;
    - calcula NOX = NO + NO2 somente quando ambos possuem
      valor no mesmo DATETIME;
    - quando apenas NO ou NO2 possui valor, NOX recebe NaN;
    - atualiza a unidade do NOX com a unidade comum de NO e NO2.
    """

    # ==========================================================
    # 1. LEITURA
    # ==========================================================

    # header=None é importante para preservar colunas duplicadas
    df = pd.read_csv(
        caminho_arquivo,
        dtype=str,
        header=None
    )

    # A primeira linha contém os nomes das colunas
    nomes_colunas = (
        df.iloc[0]
        .astype(str)
        .str.strip()
        .tolist()
    )

    # Remove a linha dos nomes
    df = df.iloc[1:].reset_index(drop=True)

    # Recoloca os nomes, mantendo duplicados
    df.columns = nomes_colunas

    caminho_dicionario = (
        "/home/nobre/Notebooks/RQAr/"
        "dicionarios/CODIGO_POLUENTES.csv"
    )

    CODIGO_POLUENTE = pd.read_csv(
        caminho_dicionario,
        dtype=str
    )

    # ==========================================================
    # 2. PADRONIZA NOMES DAS COLUNAS DO DICIONÁRIO
    # ==========================================================

    CODIGO_POLUENTE.columns = (
        CODIGO_POLUENTE.columns
        .astype(str)
        .str.strip()
    )

    # ==========================================================
    # 3. VERIFICA COLUNAS OBRIGATÓRIAS
    # ==========================================================

    if "DATETIME" not in df.columns:

        raise ValueError(
            "A coluna DATETIME não existe no arquivo."
        )

    colunas_dicionario = [
        "POLUENTE",
        "COD_POLUENTE"
    ]

    for coluna in colunas_dicionario:

        if coluna not in CODIGO_POLUENTE.columns:

            raise ValueError(
                f"A coluna '{coluna}' não existe "
                f"no CODIGO_POLUENTES."
            )

    # ==========================================================
    # 4. IDENTIFICA OS CÓDIGOS DE NO, NO2 E NOX
    # ==========================================================

    dicionario_poluentes = CODIGO_POLUENTE.copy()

    dicionario_poluentes["POLUENTE"] = (
        dicionario_poluentes["POLUENTE"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    def obtem_codigo(nome_poluente):

        registros = dicionario_poluentes[
            dicionario_poluentes["POLUENTE"]
            == nome_poluente
        ]

        if registros.empty:

            raise ValueError(
                f"O poluente '{nome_poluente}' "
                f"não foi encontrado no dicionário."
            )

        codigo = str(
            registros.iloc[0]["COD_POLUENTE"]
        ).strip()

        codigo = codigo.zfill(3)

        return codigo

    codigo_no = obtem_codigo("NO")
    codigo_no2 = obtem_codigo("NO2")
    codigo_nox = obtem_codigo("NOX")

    print("Códigos identificados:")

    print(f"  NO  → {codigo_no}")
    print(f"  NO2 → {codigo_no2}")
    print(f"  NOX → {codigo_nox}")

    # ==========================================================
    # 5. CONVERTE DATETIME
    # ==========================================================

    df["DATETIME"] = pd.to_datetime(
        df["DATETIME"],
        errors="coerce"
    )

    if df["DATETIME"].isna().any():

        quantidade = df["DATETIME"].isna().sum()

        raise ValueError(
            f"Foram encontrados {quantidade} "
            f"DATETIME inválidos."
        )

    # ==========================================================
    # 6. IDENTIFICA AS COLUNAS DE ESTAÇÕES
    # ==========================================================

    # Trabalhamos com POSIÇÃO para não perder colunas duplicadas
    colunas_estacoes = []

    for posicao, coluna in enumerate(df.columns):

        if coluna == "DATETIME":
            continue

        if coluna.startswith("UNIDADE_"):
            continue

        if coluna.startswith("QAQC_"):
            continue

        if len(str(coluna)) >= 3:

            colunas_estacoes.append(
                (posicao, str(coluna))
            )

    # ==========================================================
    # 7. IDENTIFICA TODAS AS COLUNAS DE NO, NO2 E NOX
    # ==========================================================

    colunas_no = [
        (posicao, coluna)
        for posicao, coluna in colunas_estacoes
        if coluna[-3:].zfill(3) == codigo_no
    ]

    colunas_no2 = [
        (posicao, coluna)
        for posicao, coluna in colunas_estacoes
        if coluna[-3:].zfill(3) == codigo_no2
    ]

    colunas_nox = [
        (posicao, coluna)
        for posicao, coluna in colunas_estacoes
        if coluna[-3:].zfill(3) == codigo_nox
    ]

    print("\nColunas encontradas:")

    print(f"NO  : {len(colunas_no)}")
    print(f"NO2 : {len(colunas_no2)}")
    print(f"NOX : {len(colunas_nox)}")

    # ==========================================================
    # 8. IDENTIFICA AS ESTAÇÕES PELO PREFIXO
    # ==========================================================

    prefixos_estacoes = set()

    for _, coluna in (
        colunas_no
        + colunas_no2
        + colunas_nox
    ):

        prefixo = coluna[:6]

        prefixos_estacoes.add(prefixo)

    # ==========================================================
    # 9. PROCESSA CADA ESTAÇÃO
    # ==========================================================

    for prefixo in sorted(prefixos_estacoes):

        print("\n" + "=" * 70)
        print(f"Processando estação: {prefixo}")

        no_estacao = [
            (posicao, coluna)
            for posicao, coluna in colunas_no
            if coluna[:6] == prefixo
        ]

        no2_estacao = [
            (posicao, coluna)
            for posicao, coluna in colunas_no2
            if coluna[:6] == prefixo
        ]

        nox_estacao = [
            (posicao, coluna)
            for posicao, coluna in colunas_nox
            if coluna[:6] == prefixo
        ]

        if not no_estacao:

            print(f"⚠ {prefixo}: NO não encontrado.")
            continue

        if not no2_estacao:

            print(f"⚠ {prefixo}: NO2 não encontrado.")
            continue

        if len(no_estacao) > 1:

            raise ValueError(
                f"A estação {prefixo} possui "
                f"mais de uma coluna de NO: "
                f"{no_estacao}"
            )

        if len(no2_estacao) > 1:

            raise ValueError(
                f"A estação {prefixo} possui "
                f"mais de uma coluna de NO2: "
                f"{no2_estacao}"
            )

        pos_no, coluna_no = no_estacao[0]
        pos_no2, coluna_no2 = no2_estacao[0]

        # ======================================================
        # 10. IDENTIFICA OU CRIA NOX
        # ======================================================

        if nox_estacao:

            if len(nox_estacao) > 1:

                raise ValueError(
                    f"A estação {prefixo} possui "
                    f"mais de uma coluna de NOX: "
                    f"{nox_estacao}"
                )

            pos_nox, coluna_nox = nox_estacao[0]

            print(
                f"NOX encontrado: {coluna_nox}"
            )

        else:

            coluna_nox = (
                f"{prefixo}{codigo_nox}"
            )

            print("NOX não encontrado.")
            print(f"→ Criando coluna {coluna_nox}")

            df[coluna_nox] = pd.NA

            pos_nox = len(df.columns) - 1

        # ======================================================
        # 11. IDENTIFICA AS COLUNAS DE UNIDADE
        # ======================================================

        coluna_unidade_no = (
            f"UNIDADE_{coluna_no}"
        )

        coluna_unidade_no2 = (
            f"UNIDADE_{coluna_no2}"
        )

        coluna_unidade_nox = (
            f"UNIDADE_{coluna_nox}"
        )

        if coluna_unidade_no not in df.columns:

            raise ValueError(
                f"A coluna {coluna_unidade_no} "
                f"não existe."
            )

        if coluna_unidade_no2 not in df.columns:

            raise ValueError(
                f"A coluna {coluna_unidade_no2} "
                f"não existe."
            )

        # ======================================================
        # 12. VERIFICA SE AS UNIDADES SÃO IGUAIS
        # ======================================================

        unidades_no = (
            df[coluna_unidade_no]
            .dropna()
            .astype(str)
            .str.strip()
        )

        unidades_no2 = (
            df[coluna_unidade_no2]
            .dropna()
            .astype(str)
            .str.strip()
        )

        unidades_no = unidades_no[
            ~unidades_no.str.lower().isin(
                ["", "nan", "none", "nat"]
            )
        ]

        unidades_no2 = unidades_no2[
            ~unidades_no2.str.lower().isin(
                ["", "nan", "none", "nat"]
            )
        ]

        if unidades_no.empty:

            print(
                f"⚠ {prefixo}: NO não possui unidade."
            )

            continue

        if unidades_no2.empty:

            print(
                f"⚠ {prefixo}: NO2 não possui unidade."
            )

            continue

        unidade_no = unidades_no.iloc[0]
        unidade_no2 = unidades_no2.iloc[0]

        if unidade_no.lower() != unidade_no2.lower():

            raise ValueError(
                f"Unidades diferentes para {prefixo}!\n"
                f"NO  ({coluna_no}): {unidade_no}\n"
                f"NO2 ({coluna_no2}): {unidade_no2}\n"
                f"Não é possível calcular NOX."
            )

        unidade_nox = unidade_no

        print(
            f"Unidade verificada: {unidade_nox}"
        )

        # ======================================================
        # 13. CONVERTE NO E NO2 PARA NUMÉRICO
        # ======================================================

        valores_no = pd.to_numeric(
            df.iloc[:, pos_no],
            errors="coerce"
        )

        valores_no2 = pd.to_numeric(
            df.iloc[:, pos_no2],
            errors="coerce"
        )
        # ======================================================
        # 14. IGNORA VALORES ESPECIAIS
        # ======================================================

        valores_especiais = [
            "985",
            "998",
            "999",
            "9999",
            "-999",
            "-9999",
            "8888",
            "7777"
        ]

        valores_no = valores_no.mask(
            df.iloc[:, pos_no].isin(valores_especiais)
        )

        valores_no2 = valores_no2.mask(
            df.iloc[:, pos_no2].isin(valores_especiais)
        )
                
        # ======================================================
        # 14. VERIFICA MEDIÇÕES HORÁRIAS
        # ======================================================

        possui_no = valores_no.notna()
        possui_no2 = valores_no2.notna()

        ambos_medidos = (
            possui_no
            & possui_no2
        )

        somente_no = (
            possui_no
            & ~possui_no2
        )

        somente_no2 = (
            ~possui_no
            & possui_no2
        )

        nenhum = (
            ~possui_no
            & ~possui_no2
        )

        # ======================================================
        # 15. CALCULA NOX
        # ======================================================

        valores_nox = pd.Series(
            pd.NA,
            index=df.index,
            dtype="Float64"
        )

        valores_nox.loc[ambos_medidos] = (
            valores_no.loc[ambos_medidos]
            +
            valores_no2.loc[ambos_medidos]
        )

        df.iloc[:, pos_nox] = valores_nox

        # ======================================================
        # 16. ATUALIZA UNIDADE DO NOX
        # ======================================================

        if coluna_unidade_nox not in df.columns:

            df[coluna_unidade_nox] = pd.NA

        df[coluna_unidade_nox] = unidade_nox

        # ======================================================
        # 17. RELATÓRIO
        # ======================================================

        print(f"NO  : {coluna_no}")
        print(f"NO2 : {coluna_no2}")
        print(f"NOX : {coluna_nox}")

        print(
            f"Total de horários: {len(df)}"
        )

        print(
            f"NO e NO2 medidos: "
            f"{ambos_medidos.sum()}"
        )

        print(
            f"Somente NO medido: "
            f"{somente_no.sum()}"
        )

        print(
            f"Somente NO2 medido: "
            f"{somente_no2.sum()}"
        )

        print(
            f"Nenhum dos dois medido: "
            f"{nenhum.sum()}"
        )

        print(
            f"NOX calculado: "
            f"{valores_nox.notna().sum()}"
        )

        print(
            f"NOX = NaN: "
            f"{valores_nox.isna().sum()}"
        )

    # ==========================================================
    # 18. SALVA
    # ==========================================================

    df.to_csv(
        caminho_arquivo,
        index=False,
        encoding="utf-8",
        sep=","
    )

    print("\n" + "=" * 70)
    print("✓ NOX atualizado com sucesso!")
    print(
        f"Arquivo atualizado em:\n{caminho_arquivo}"
    )