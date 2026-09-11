import os
import pandas as pd


def preencher_dados_aprovados(
    UF,
    ANO_ANTERIOR,
    ANO_ATUAL,
    base="/home/nobre/Notebooks/RQAr/dados/dados_formatados"
):
    """
    Preenche os dados do ano atual utilizando informações do ano anterior.

    REGRAS
    ------

    APROVADO = "S"
    ----------------
    - Match normal.
    - Usa o ID_MMA do ano anterior.
    - Preenche o ID_MMA em todas as linhas daquele ID_OEMA no ano atual.
    - Depois, preenche os demais dados somente na combinação
      ID_OEMA + POLUENTE.
    - Só preenche campos que estejam vazios.
    - Nunca sobrescreve dados existentes.

    APROVADO = "M"
    ----------------
    - Match da mesma estação, mas com alguma diferença
      (por exemplo, POLUENTE diferente).
    - Serve SOMENTE para identificar e preencher o ID_MMA.
    - Não preenche nenhuma outra coluna.
    - O ID_MMA é aplicado a todas as linhas daquele ID_OEMA no ano atual
      que ainda estiverem sem ID_MMA.
    - Não depende do POLUENTE.

    APROVADO = "N" ou vazio
    -----------------------
    - Não faz nenhum preenchimento.

    ARQUIVOS
    --------
    - O arquivo de matches é somente lido.
    - O arquivo de não encontrados não é alterado.
    - Somente o arquivo do ano atual é alterado.
    """

    # ==========================================================
    # CONFIGURAÇÃO
    # ==========================================================

    UF = str(UF).upper().strip()

    # ==========================================================
    # CAMINHOS
    # ==========================================================

    arquivo_anterior = (
        f"{base}/{ANO_ANTERIOR}/rede/"
        f"{UF}_Rede_{ANO_ANTERIOR}.csv"
    )

    arquivo_atual = (
        f"{base}/{ANO_ATUAL}/rede/"
        f"{UF}_Rede_{ANO_ATUAL}.csv"
    )

    pasta_comparacao = (
        f"{base}/{ANO_ATUAL}/rede/"
        f"comparando_tabelas/{UF}"
    )

    arquivo_matches = os.path.join(
        pasta_comparacao,
        f"matches_{UF}_{ANO_ANTERIOR}_{ANO_ATUAL}.csv"
    )

    # ==========================================================
    # VERIFICAÇÃO
    # ==========================================================

    for arquivo, nome in [
        (arquivo_anterior, "ano anterior"),
        (arquivo_atual, "ano atual"),
        (arquivo_matches, "matches"),
    ]:

        if not os.path.exists(arquivo):

            raise FileNotFoundError(
                f"Arquivo do {nome} não encontrado:\n"
                f"{arquivo}"
            )

    # ==========================================================
    # LEITURA
    # ==========================================================

    df_anterior = pd.read_csv(
        arquivo_anterior,
        dtype=str
    )

    df_atual = pd.read_csv(
        arquivo_atual,
        dtype=str
    )

    matches = pd.read_csv(
        arquivo_matches,
        dtype=str
    )

    # ==========================================================
    # LIMPA NOMES DAS COLUNAS
    # ==========================================================

    df_anterior.columns = (
        df_anterior.columns
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
    )

    df_atual.columns = (
        df_atual.columns
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
    )

    matches.columns = (
        matches.columns
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
    )

    # ==========================================================
    # CORRIGE PRIMEIRA COLUNA DO MATCH
    # ==========================================================

    if "Unnamed: 0" in matches.columns:

        matches = matches.rename(
            columns={
                "Unnamed: 0":
                    f"ID_OEMA_{ANO_ANTERIOR}"
            }
        )

    # ==========================================================
    # COLUNAS NECESSÁRIAS
    # ==========================================================

    for coluna in [
        "ID_OEMA",
        "POLUENTE",
        "ID_MMA"
    ]:

        if coluna not in df_anterior.columns:

            raise ValueError(
                f"Coluna '{coluna}' não encontrada "
                f"no arquivo do ano {ANO_ANTERIOR}."
            )

        if coluna not in df_atual.columns:

            raise ValueError(
                f"Coluna '{coluna}' não encontrada "
                f"no arquivo do ano {ANO_ATUAL}."
            )

    colunas_match = [
        f"ID_OEMA_{ANO_ANTERIOR}",
        f"ID_OEMA_{ANO_ATUAL}",
        "APROVADO"
    ]

    for coluna in colunas_match:

        if coluna not in matches.columns:

            raise ValueError(
                f"Coluna '{coluna}' não encontrada "
                f"no arquivo de matches.\n\n"
                f"Colunas encontradas:\n"
                f"{matches.columns.tolist()}"
            )

    # ==========================================================
    # NORMALIZAÇÃO
    # ==========================================================

    def limpar(valor):

        if pd.isna(valor):
            return ""

        return str(valor).strip()

    for df in [
        df_anterior,
        df_atual
    ]:

        for coluna in [
            "ID_OEMA",
            "POLUENTE",
            "ID_MMA"
        ]:

            df[coluna] = (
                df[coluna]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    for coluna in [
        f"ID_OEMA_{ANO_ANTERIOR}",
        f"ID_OEMA_{ANO_ATUAL}",
        "APROVADO"
    ]:

        matches[coluna] = (
            matches[coluna]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # ==========================================================
    # SEPARA OS MATCHES
    # ==========================================================

    matches_s = matches[
        matches["APROVADO"]
        .str.upper()
        .eq("S")
    ].copy()

    matches_m = matches[
        matches["APROVADO"]
        .str.upper()
        .eq("M")
    ].copy()

    print(
        f"Matches aprovados (S): {len(matches_s)}"
    )

    print(
        f"Matches somente ID_MMA (M): {len(matches_m)}"
    )

    # ==========================================================
    # ETAPA 1
    # MATCH S
    #
    # ID_OEMA → ID_MMA
    # ==========================================================

    mapa_id_mma = {}

    for _, match in matches_s.iterrows():

        id_oema_anterior = limpar(
            match[f"ID_OEMA_{ANO_ANTERIOR}"]
        )

        id_oema_atual = limpar(
            match[f"ID_OEMA_{ANO_ATUAL}"]
        )

        if not id_oema_anterior:
            continue

        if not id_oema_atual:
            continue

        # ------------------------------------------------------
        # PROCURA ID_MMA NO ANO ANTERIOR
        # ------------------------------------------------------

        linhas_anterior = df_anterior[
            df_anterior["ID_OEMA"]
            .eq(id_oema_anterior)
        ]

        if linhas_anterior.empty:
            continue

        # ------------------------------------------------------
        # PEGA ID_MMA PREENCHIDO
        # ------------------------------------------------------

        ids_mma = (
            linhas_anterior["ID_MMA"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        ids_mma = ids_mma[
            (ids_mma != "")
            &
            (
                ~ids_mma.str.lower().isin([
                    "nan",
                    "none",
                    "nao declarado",
                    "não declarado"
                ])
            )
        ]

        if ids_mma.empty:
            continue

        id_mma = ids_mma.iloc[0]

        mapa_id_mma[id_oema_atual] = id_mma

    # ==========================================================
    # ETAPA 2
    # MATCH M
    #
    # MESMA ESTAÇÃO
    # SOMENTE ID_MMA
    # ==========================================================

    for _, match in matches_m.iterrows():

        id_oema_anterior = limpar(
            match[f"ID_OEMA_{ANO_ANTERIOR}"]
        )

        id_oema_atual = limpar(
            match[f"ID_OEMA_{ANO_ATUAL}"]
        )

        if not id_oema_anterior:
            continue

        if not id_oema_atual:
            continue

        # ------------------------------------------------------
        # PROCURA ID_MMA NO ANO ANTERIOR
        # ------------------------------------------------------

        linhas_anterior = df_anterior[
            df_anterior["ID_OEMA"]
            .eq(id_oema_anterior)
        ]

        if linhas_anterior.empty:
            continue

        # ------------------------------------------------------
        # PEGA ID_MMA PREENCHIDO
        # ------------------------------------------------------

        ids_mma = (
            linhas_anterior["ID_MMA"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        ids_mma = ids_mma[
            (ids_mma != "")
            &
            (
                ~ids_mma.str.lower().isin([
                    "nan",
                    "none",
                    "nao declarado",
                    "não declarado"
                ])
            )
        ]

        if ids_mma.empty:
            continue

        id_mma = ids_mma.iloc[0]

        # ------------------------------------------------------
        # MAPEIA PARA O ID_OEMA ATUAL
        #
        # O M não preenche outros dados.
        # Apenas permite identificar o ID_MMA.
        # ------------------------------------------------------

        mapa_id_mma[id_oema_atual] = id_mma

    # ==========================================================
    # ETAPA 3
    # PREENCHE ID_MMA
    #
    # S E M
    # ==========================================================

    total_id_mma_s = 0
    total_id_mma_m = 0

    # ----------------------------------------------------------
    # PRIMEIRO: ID_MMA DOS MATCHES S
    # ----------------------------------------------------------

    mapa_s = {}

    for _, match in matches_s.iterrows():

        id_oema_anterior = limpar(
            match[f"ID_OEMA_{ANO_ANTERIOR}"]
        )

        id_oema_atual = limpar(
            match[f"ID_OEMA_{ANO_ATUAL}"]
        )

        if not id_oema_anterior or not id_oema_atual:
            continue

        linhas_anterior = df_anterior[
            df_anterior["ID_OEMA"]
            .eq(id_oema_anterior)
        ]

        ids_mma = (
            linhas_anterior["ID_MMA"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        ids_mma = ids_mma[
            (ids_mma != "")
            &
            (
                ~ids_mma.str.lower().isin([
                    "nan",
                    "none",
                    "nao declarado",
                    "não declarado"
                ])
            )
        ]

        if not ids_mma.empty:

            mapa_s[id_oema_atual] = ids_mma.iloc[0]

    # ----------------------------------------------------------
    # APLICA S
    # ----------------------------------------------------------

    for id_oema, id_mma in mapa_s.items():

        mascara_oema = (
            df_atual["ID_OEMA"]
            .eq(id_oema)
        )

        mascara_vazio = (
            df_atual["ID_MMA"]
            .isna()
            |
            df_atual["ID_MMA"]
            .eq("")
        )

        mascara = (
            mascara_oema
            &
            mascara_vazio
        )

        quantidade = mascara.sum()

        if quantidade > 0:

            df_atual.loc[
                mascara,
                "ID_MMA"
            ] = id_mma

            total_id_mma_s += quantidade

    # ----------------------------------------------------------
    # SEGUNDO: APLICA M
    #
    # SOMENTE SE AINDA ESTIVER VAZIO
    # ----------------------------------------------------------

    mapa_m = {}

    for _, match in matches_m.iterrows():

        id_oema_anterior = limpar(
            match[f"ID_OEMA_{ANO_ANTERIOR}"]
        )

        id_oema_atual = limpar(
            match[f"ID_OEMA_{ANO_ATUAL}"]
        )

        if not id_oema_anterior or not id_oema_atual:
            continue

        linhas_anterior = df_anterior[
            df_anterior["ID_OEMA"]
            .eq(id_oema_anterior)
        ]

        ids_mma = (
            linhas_anterior["ID_MMA"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        ids_mma = ids_mma[
            (ids_mma != "")
            &
            (
                ~ids_mma.str.lower().isin([
                    "nan",
                    "none",
                    "nao declarado",
                    "não declarado"
                ])
            )
        ]

        if not ids_mma.empty:

            mapa_m[id_oema_atual] = ids_mma.iloc[0]

    # ----------------------------------------------------------
    # APLICA M
    # ----------------------------------------------------------

    for id_oema, id_mma in mapa_m.items():

        mascara_oema = (
            df_atual["ID_OEMA"]
            .eq(id_oema)
        )

        mascara_vazio = (
            df_atual["ID_MMA"]
            .isna()
            |
            df_atual["ID_MMA"]
            .eq("")
        )

        mascara = (
            mascara_oema
            &
            mascara_vazio
        )

        quantidade = mascara.sum()

        if quantidade > 0:

            df_atual.loc[
                mascara,
                "ID_MMA"
            ] = id_mma

            total_id_mma_m += quantidade

    # ==========================================================
    # ETAPA 4
    # DEMAIS DADOS
    #
    # SOMENTE MATCHES S
    # ==========================================================

    total_preenchimentos = 0

    for _, match in matches_s.iterrows():

        id_oema_anterior = limpar(
            match[f"ID_OEMA_{ANO_ANTERIOR}"]
        )

        id_oema_atual = limpar(
            match[f"ID_OEMA_{ANO_ATUAL}"]
        )

        # ------------------------------------------------------
        # PEGA POLUENTE
        # ------------------------------------------------------

        if "POLUENTE_{}".format(ANO_ATUAL) in matches.columns:

            poluente = limpar(
                match[f"POLUENTE_{ANO_ATUAL}"]
            )

        elif "POLUENTE" in matches.columns:

            poluente = limpar(
                match["POLUENTE"]
            )

        else:

            poluente = ""

        if (
            not id_oema_anterior
            or not id_oema_atual
            or not poluente
        ):
            continue

        # ======================================================
        # LOCALIZA ANO ANTERIOR
        # ======================================================

        idx_anterior = df_anterior[
            (
                df_anterior["ID_OEMA"]
                .eq(id_oema_anterior)
            )
            &
            (
                df_anterior["POLUENTE"]
                .eq(poluente)
            )
        ].index

        if len(idx_anterior) == 0:
            continue

        idx_anterior = idx_anterior[0]

        # ======================================================
        # LOCALIZA ANO ATUAL
        # ======================================================

        idx_atual = df_atual[
            (
                df_atual["ID_OEMA"]
                .eq(id_oema_atual)
            )
            &
            (
                df_atual["POLUENTE"]
                .eq(poluente)
            )
        ].index

        if len(idx_atual) == 0:
            continue

        idx_atual = idx_atual[0]

        # ======================================================
        # COPIA DEMAIS COLUNAS
        # ======================================================

        for coluna in df_atual.columns:

            if coluna in {
                "ID_OEMA",
                "ID_MMA",
                "POLUENTE"
            }:
                continue

            if coluna not in df_anterior.columns:
                continue

            valor_atual = df_atual.at[
                idx_atual,
                coluna
            ]

            valor_anterior = df_anterior.at[
                idx_anterior,
                coluna
            ]

            atual_vazio = (
                pd.isna(valor_atual)
                or str(valor_atual).strip() == ""
                or str(valor_atual).strip().lower()
                in [
                    "nan",
                    "none"
                ]
            )

            anterior_preenchido = (
                not pd.isna(valor_anterior)
                and str(valor_anterior).strip() != ""
                and str(valor_anterior).strip().lower()
                not in [
                    "nan",
                    "none",
                    "nao declarado",
                    "não declarado"
                ]
            )

            if (
                atual_vazio
                and anterior_preenchido
            ):

                df_atual.at[
                    idx_atual,
                    coluna
                ] = valor_anterior

                total_preenchimentos += 1

    # ==========================================================
    # SALVA SOMENTE O ANO ATUAL
    # ==========================================================

    df_atual.to_csv(
        arquivo_atual,
        index=False,
        encoding="utf-8-sig"
    )

    # ==========================================================
    # RESUMO
    # ==========================================================

    print(
        "\n=========================================="
    )

    print(
        "PREENCHIMENTO CONCLUÍDO"
    )

    print(
        "=========================================="
    )

    print(
        f"UF: {UF}"
    )

    print(
        f"Ano anterior: {ANO_ANTERIOR}"
    )

    print(
        f"Ano atual: {ANO_ATUAL}"
    )

    print(
        f"Matches S: {len(matches_s)}"
    )

    print(
        f"Matches M: {len(matches_m)}"
    )

    print(
        f"ID_MMA preenchidos por S: "
        f"{total_id_mma_s}"
    )

    print(
        f"ID_MMA preenchidos por M: "
        f"{total_id_mma_m}"
    )

    print(
        f"Demais valores preenchidos por S: "
        f"{total_preenchimentos}"
    )

    print(
        "------------------------------------------"
    )

    print(
        "Regra M: somente ID_MMA foi preenchido."
    )

    print(
        "Regra S: ID_MMA + demais campos."
    )

    print(
        "------------------------------------------"
    )

    print(
        f"Arquivo atualizado:"
        f"\n{arquivo_atual}"
    )

    print(
        "=========================================="
    )

    return df_atual
