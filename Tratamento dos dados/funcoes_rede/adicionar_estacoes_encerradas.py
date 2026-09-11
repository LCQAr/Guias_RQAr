import os
import pandas as pd


def adicionar_estacoes_encerradas(
    UF,
    ANO_ANTERIOR,
    ANO_ATUAL,
    substituicoes=None,
    BASE="/home/nobre/Notebooks/RQAr/dados/dados_formatados",
    sobrescrever=True,
):
    """
    Adiciona à rede do ano atual as linhas da rede do ano anterior
    que aparecem no arquivo de não encontrados.

    O match inicial é feito por:
        ID_OEMA_2024 + POLUENTE_2024
        com
        ID_OEMA + POLUENTE da rede anterior.

    Para cada estação encerrada:

    - Tenta localizar a estação correspondente pelo ID_OEMA na rede atual;
    - Se houver substituição em 'substituicoes', utiliza o novo ID_OEMA;
    - Se encontrar pelo ID_OEMA, ID_OEMA e ID_OEMA_ORIGINAL recebem
      os valores da rede atual;
    - Independentemente de encontrar ou não pelo ID_OEMA, verifica
      se o ID_MMA da estação encerrada já existe na rede atual;
    - Quando o ID_MMA existir, os campos vazios da estação encerrada
      são preenchidos com os valores da linha correspondente ao
      mesmo ID_MMA;
    - Valores que já existem na rede anterior NÃO são substituídos;
    - O preenchimento pelo ID_MMA não altera:
        INICIO
        FIM
        ELEVACAO
        BASE_DADOS
        ANOS_MONITORADOS
    - Campos específicos ainda vazios podem ser preenchidos pela
      correspondência do ID_OEMA;
    - STATUS recebe "Inativo";
    - FIM recebe 31/12/ANO_ANTERIOR;
    - Evita duplicidades pela combinação ID_OEMA + POLUENTE.

    O arquivo de não encontrados NÃO é alterado.
    """

    # ==========================================================
    # CAMINHOS
    # ==========================================================

    arquivo_nao_encontrados = (
        f"{BASE}/{ANO_ATUAL}/rede/comparando_tabelas/"
        f"{UF}/{UF}_nao_encontrados_{ANO_ANTERIOR}_{ANO_ATUAL}.csv"
    )

    arquivo_anterior = (
        f"{BASE}/{ANO_ANTERIOR}/rede/"
        f"{UF}_Rede_{ANO_ANTERIOR}.csv"
    )

    arquivo_atual = (
        f"{BASE}/{ANO_ATUAL}/rede/"
        f"{UF}_Rede_{ANO_ATUAL}.csv"
    )

    # ==========================================================
    # VERIFICA ARQUIVOS
    # ==========================================================

    for arquivo in [
        arquivo_nao_encontrados,
        arquivo_anterior,
        arquivo_atual,
    ]:
        if not os.path.exists(arquivo):
            raise FileNotFoundError(
                f"Arquivo não encontrado:\n{arquivo}"
            )

    # ==========================================================
    # LEITURA
    # ==========================================================

    df_nao = pd.read_csv(
        arquivo_nao_encontrados,
        encoding="utf-8-sig"
    )

    df_anterior = pd.read_csv(
        arquivo_anterior,
        encoding="utf-8-sig"
    )

    df_atual = pd.read_csv(
        arquivo_atual,
        encoding="utf-8-sig"
    )

    # ==========================================================
    # COLUNAS NECESSÁRIAS
    # ==========================================================

    for coluna in [
        "ID_OEMA_2024",
        "POLUENTE_2024",
    ]:
        if coluna not in df_nao.columns:
            raise KeyError(
                f"A coluna '{coluna}' não existe em:\n"
                f"{arquivo_nao_encontrados}"
            )

    for coluna in [
        "ID_OEMA",
        "POLUENTE",
    ]:
        if coluna not in df_anterior.columns:
            raise KeyError(
                f"A coluna '{coluna}' não existe em:\n"
                f"{arquivo_anterior}"
            )

        if coluna not in df_atual.columns:
            raise KeyError(
                f"A coluna '{coluna}' não existe em:\n"
                f"{arquivo_atual}"
            )

    # ==========================================================
    # REMOVE LINHAS INVÁLIDAS
    # ==========================================================

    df_nao = df_nao[
        df_nao["ID_OEMA_2024"].notna()
        & df_nao["POLUENTE_2024"].notna()
    ].copy()

    if df_nao.empty:
        print(
            "Nenhuma combinação válida encontrada "
            "no arquivo de não encontrados."
        )
        return

    # ==========================================================
    # DICIONÁRIO
    # ==========================================================

    if substituicoes is None:
        substituicoes = {}

    # ==========================================================
    # PADRONIZA CHAVES
    # ==========================================================

    df_nao["_ID_MATCH"] = (
        df_nao["ID_OEMA_2024"]
        .astype(str)
        .str.strip()
    )

    df_nao["_POLUENTE_MATCH"] = (
        df_nao["POLUENTE_2024"]
        .astype(str)
        .str.strip()
    )

    df_anterior["_ID_MATCH"] = (
        df_anterior["ID_OEMA"]
        .astype(str)
        .str.strip()
    )

    df_anterior["_POLUENTE_MATCH"] = (
        df_anterior["POLUENTE"]
        .astype(str)
        .str.strip()
    )

    # ==========================================================
    # CHAVES PARA LOCALIZAR AS LINHAS DO ANO ANTERIOR
    # ==========================================================

    chaves = set(
        zip(
            df_nao["_ID_MATCH"],
            df_nao["_POLUENTE_MATCH"],
        )
    )

    # ==========================================================
    # LOCALIZA LINHAS DO ANO ANTERIOR
    # ==========================================================

    adicionar = df_anterior[
        df_anterior.apply(
            lambda x: (
                x["_ID_MATCH"],
                x["_POLUENTE_MATCH"],
            ) in chaves,
            axis=1,
        )
    ].copy()

    adicionar.drop(
        columns=[
            "_ID_MATCH",
            "_POLUENTE_MATCH",
        ],
        inplace=True,
    )

    if adicionar.empty:
        print(
            "Nenhuma linha correspondente foi encontrada "
            "na rede do ano anterior."
        )
        return

    # ==========================================================
    # PREPARA ID DA REDE ATUAL
    # ==========================================================

    df_atual["_ID_MATCH"] = (
        df_atual["ID_OEMA"]
        .astype(str)
        .str.strip()
    )

    # ==========================================================
    # COLUNAS QUE NÃO PODEM SER PREENCHIDAS PELO ID_MMA
    # ==========================================================

    colunas_nao_substituir = {
        "INICIO",
        "FIM",
        "ELEVACAO",
        "BASE_DADOS",
        "ANOS_MONITORADOS",
    }

    # ==========================================================
    # COLUNAS QUE PODEM SER COMPLETADAS PELO ID_OEMA
    # ==========================================================

    colunas_preencher = [
        "CIDADE",
        "CD_MUN",
        "LATITUDE",
        "LONGITUDE",
        "COD_UF_IBGE",
        "CATEGORIA",
        "FUNCIONAMENTO",
    ]

    # ==========================================================
    # CONTADORES
    # ==========================================================

    total_id_oema_encontrados = 0
    total_id_mma_encontrados = 0
    total_campos_id_mma = 0
    total_campos_id_oema = 0

    # ==========================================================
    # PROCESSA CADA LINHA
    # ==========================================================

    for indice in adicionar.index:

        id_2024 = str(
            adicionar.loc[indice, "ID_OEMA"]
        ).strip()

        # ------------------------------------------------------
        # ID PARA PROCURAR NA REDE ATUAL
        # ------------------------------------------------------

        id_para_busca = substituicoes.get(
            id_2024,
            id_2024
        )

        correspondencias = df_atual[
            df_atual["_ID_MATCH"] == id_para_busca
        ]

        # ------------------------------------------------------
        # LINHA ENCONTRADA PELO ID_OEMA
        # ------------------------------------------------------

        if not correspondencias.empty:

            total_id_oema_encontrados += 1

            linha_oema = correspondencias.iloc[0]

            # ==================================================
            # ID_OEMA VEM DO ANO ATUAL
            # ==================================================

            adicionar.loc[
                indice,
                "ID_OEMA"
            ] = linha_oema["ID_OEMA"]

            # ==================================================
            # ID_OEMA_ORIGINAL VEM DO ANO ATUAL
            # ==================================================

            if (
                "ID_OEMA_ORIGINAL" in adicionar.columns
                and "ID_OEMA_ORIGINAL" in df_atual.columns
            ):

                adicionar.loc[
                    indice,
                    "ID_OEMA_ORIGINAL"
                ] = linha_oema["ID_OEMA_ORIGINAL"]

        else:

            linha_oema = None

        # ======================================================
        # PROCURA PELO ID_MMA
        #
        # IMPORTANTE:
        # ISSO ACONTECE MESMO QUANDO O ID_OEMA NÃO FOI ENCONTRADO
        # ======================================================

        if (
            "ID_MMA" in adicionar.columns
            and "ID_MMA" in df_atual.columns
        ):

            id_mma = adicionar.loc[
                indice,
                "ID_MMA"
            ]

            id_mma_valido = (
                not pd.isna(id_mma)
                and str(id_mma).strip() != ""
                and str(id_mma).strip().lower() != "nan"
            )

            if id_mma_valido:

                id_mma_match = str(
                    id_mma
                ).strip()

                correspondencias_mma = df_atual[
                    df_atual["ID_MMA"]
                    .astype(str)
                    .str.strip()
                    == id_mma_match
                ]

                if not correspondencias_mma.empty:

                    total_id_mma_encontrados += 1

                    # Primeira linha encontrada com o mesmo ID_MMA
                    linha_mma = correspondencias_mma.iloc[0]

                    # ==================================================
                    # TODAS AS COLUNAS EM COMUM
                    # ==================================================

                    colunas_comuns = (
                        set(adicionar.columns)
                        & set(df_atual.columns)
                    )

                    for coluna in colunas_comuns:

                        # ----------------------------------------------
                        # NÃO ALTERA ESSAS COLUNAS
                        # ----------------------------------------------

                        if coluna in colunas_nao_substituir:
                            continue

                        # ----------------------------------------------
                        # NÃO ALTERA ID_OEMA
                        # ----------------------------------------------

                        if coluna == "ID_OEMA":
                            continue

                        # ----------------------------------------------
                        # NÃO ALTERA ID_OEMA_ORIGINAL
                        # ----------------------------------------------

                        if coluna == "ID_OEMA_ORIGINAL":
                            continue

                        # ----------------------------------------------
                        # VALORES
                        # ----------------------------------------------

                        valor_2024 = adicionar.loc[
                            indice,
                            coluna
                        ]

                        valor_atual = linha_mma[coluna]

                        # ----------------------------------------------
                        # VERIFICA SE O VALOR DE 2024 ESTÁ VAZIO
                        # ----------------------------------------------

                        vazio_2024 = (
                            pd.isna(valor_2024)
                            or str(valor_2024).strip() == ""
                            or str(valor_2024).strip().lower() == "nan"
                        )

                        # ----------------------------------------------
                        # VERIFICA SE O VALOR ATUAL EXISTE
                        # ----------------------------------------------

                        preenchido_atual = (
                            not pd.isna(valor_atual)
                            and str(valor_atual).strip() != ""
                            and str(valor_atual).strip().lower() != "nan"
                        )

                        # ----------------------------------------------
                        # PREENCHE SOMENTE O BURACO
                        # ----------------------------------------------

                        if vazio_2024 and preenchido_atual:

                            adicionar.loc[
                                indice,
                                coluna
                            ] = valor_atual

                            total_campos_id_mma += 1

        # ======================================================
        # PREENCHE CAMPOS ESPECÍFICOS PELO ID_OEMA
        # ======================================================

        if linha_oema is not None:

            for coluna in colunas_preencher:

                if coluna not in adicionar.columns:
                    continue

                if coluna not in df_atual.columns:
                    continue

                valor_2024 = adicionar.loc[
                    indice,
                    coluna
                ]

                valor_2025 = linha_oema[coluna]

                vazio_2024 = (
                    pd.isna(valor_2024)
                    or str(valor_2024).strip() == ""
                )

                preenchido_2025 = (
                    not pd.isna(valor_2025)
                    and str(valor_2025).strip() != ""
                )

                if vazio_2024 and preenchido_2025:

                    adicionar.loc[
                        indice,
                        coluna
                    ] = valor_2025

                    total_campos_id_oema += 1

    # ==========================================================
    # REMOVE COLUNA AUXILIAR
    # ==========================================================

    df_atual.drop(
        columns=["_ID_MATCH"],
        inplace=True,
    )

    # ==========================================================
    # STATUS
    # ==========================================================

    adicionar["STATUS"] = "Inativo"

    # FIM
    # Preenche FIM somente se estiver vazia
    if "FIM" in adicionar.columns:
        mascara_fim_vazio = (
            adicionar["FIM"].isna()
            | (adicionar["FIM"].astype(str).str.strip() == "")
            | (adicionar["FIM"].astype(str).str.strip().str.lower() == "nan")
        )
    
        adicionar.loc[mascara_fim_vazio, "FIM"] = (
            f"31/12/{ANO_ANTERIOR}"
        )

    # ==========================================================
    # GARANTE MESMAS COLUNAS DA REDE ATUAL
    # ==========================================================

    for coluna in df_atual.columns:

        if coluna not in adicionar.columns:
            adicionar[coluna] = pd.NA

    adicionar = adicionar[
        df_atual.columns
    ]

    # ==========================================================
    # EVITA DUPLICATAS
    # ==========================================================

    chaves_atual = set(
        zip(
            df_atual["ID_OEMA"]
            .astype(str)
            .str.strip(),

            df_atual["POLUENTE"]
            .astype(str)
            .str.strip(),
        )
    )

    adicionar = adicionar[
        ~adicionar.apply(
            lambda x: (
                str(x["ID_OEMA"]).strip(),
                str(x["POLUENTE"]).strip(),
            ) in chaves_atual,
            axis=1,
        )
    ].copy()

    if adicionar.empty:
        print(
            "As linhas encontradas já existem "
            "na rede do ano atual."
        )
        print("Nenhuma linha foi adicionada.")
        return

    # ==========================================================
    # CONCATENA
    # ==========================================================

    df_final = pd.concat(
        [
            df_atual,
            adicionar,
        ],
        ignore_index=True,
    )

    # ==========================================================
    # SAÍDA
    # ==========================================================

    if sobrescrever:

        saida = arquivo_atual

    else:

        saida = arquivo_atual.replace(
            ".csv",
            "_com_encerradas.csv"
        )

    # ==========================================================
    # SALVA
    # ==========================================================

    df_final.to_csv(
        saida,
        index=False,
        encoding="utf-8-sig",
    )

    # ==========================================================
    # RESULTADO
    # ==========================================================

    print(
        f"{len(adicionar)} linhas adicionadas."
    )

    print(
        f"ID_OEMA encontrados na rede atual: "
        f"{total_id_oema_encontrados}"
    )

    print(
        f"ID_MMA encontrados na rede atual: "
        f"{total_id_mma_encontrados}"
    )

    print(
        f"Campos vazios preenchidos pelo ID_MMA: "
        f"{total_campos_id_mma}"
    )

    print(
        f"Campos vazios preenchidos pelo ID_OEMA: "
        f"{total_campos_id_oema}"
    )

    print(
        "STATUS = Inativo"
    )

    print(
        f"FIM = 31/12/{ANO_ANTERIOR}"
    )

    print(
        "INICIO, FIM, ELEVACAO, BASE_DADOS e "
        "ANOS_MONITORADOS não foram substituídos pelo ID_MMA."
    )

    print(
        f"Arquivo salvo em:\n{saida}"
    )