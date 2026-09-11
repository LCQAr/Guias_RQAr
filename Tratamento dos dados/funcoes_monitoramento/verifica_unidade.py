import pandas as pd
import csv


def verifica_unidade(caminho_arquivo):

    # ==========================================================
    # CAMINHOS DOS DICIONÁRIOS
    # ==========================================================

    caminho_dicionario = (
        "/home/nobre/Notebooks/RQAr/dicionarios/"
        "CODIGO_POLUENTES.csv"
    )

    caminho_conversao = (
        "/home/nobre/Notebooks/RQAr/dicionarios/"
        "conversao_unidade.csv"
    )

    # ==========================================================
    # LEITURA DO ARQUIVO
    # ==========================================================

    # Lê os nomes originais das colunas, preservando duplicadas
    with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
        leitor = csv.reader(arquivo)
        colunas_originais = next(leitor)

    # Lê o arquivo normalmente
    df = pd.read_csv(
        caminho_arquivo,
        dtype=str
    )

    # Restaura os nomes originais das colunas
    df.columns = colunas_originais

    # ==========================================================
    # LEITURA DOS DICIONÁRIOS
    # ==========================================================

    CODIGO_POLUENTE = pd.read_csv(
        caminho_dicionario,
        dtype=str
    )

    tabela_conversao = pd.read_csv(
        caminho_conversao,
        dtype=str
    )

    # ==========================================================
    # PADRONIZA NOMES DAS COLUNAS DOS DICIONÁRIOS
    # ==========================================================

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    CODIGO_POLUENTE.columns = (
        CODIGO_POLUENTE.columns
        .astype(str)
        .str.strip()
    )

    tabela_conversao.columns = (
        tabela_conversao.columns
        .astype(str)
        .str.strip()
    )

    # ==========================================================
    # MAPA COD_POLUENTE → NOME_PASTA
    # ==========================================================

    mapa_poluente = (
        CODIGO_POLUENTE
        .drop_duplicates("COD_POLUENTE")
        .set_index("COD_POLUENTE")["NOME_PASTA"]
        .to_dict()
    )

    # ==========================================================
    # VALORES QUE NÃO DEVEM SER CONVERTIDOS
    # ==========================================================

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

    # ==========================================================
    # PERCORRE AS COLUNAS DE UNIDADE
    # ==========================================================

    for posicao_unidade, coluna_unidade in enumerate(df.columns):

        if not coluna_unidade.startswith("UNIDADE_"):
            continue

        # ------------------------------------------------------
        # ID_MMA_COMPLETO
        # ------------------------------------------------------

        id_mma_completo = coluna_unidade.replace(
            "UNIDADE_",
            "",
            1
        )

        # ------------------------------------------------------
        # COLUNA DE VALOR
        # ------------------------------------------------------

        posicao_valor = posicao_unidade - 1

        if posicao_valor < 0:
            print(
                f"Atenção: não foi encontrada coluna de "
                f"valor para {id_mma_completo}."
            )
            continue

        # ======================================================
        # IDENTIFICA O COD_POLUENTE
        # ======================================================

        try:

            cod_poluente = int(
                id_mma_completo[-3:]
            )

        except ValueError:

            print(
                f"Atenção: não foi possível identificar "
                f"o COD_POLUENTE de {id_mma_completo}."
            )

            continue

        # ======================================================
        # BUSCA O POLUENTE
        # ======================================================

        poluente = mapa_poluente.get(
            str(cod_poluente)
        )

        if poluente is None:
            poluente = mapa_poluente.get(
                cod_poluente
            )

        if poluente is None:

            print(
                f"Atenção: código do poluente "
                f"{cod_poluente} não encontrado "
                f"no CODIGO_POLUENTES."
            )

            continue

        poluente = str(
            poluente
        ).strip()

        # ======================================================
        # OBTÉM A UNIDADE ATUAL
        # ======================================================

        unidades = (
            df.iloc[:, posicao_unidade]
            .dropna()
            .astype(str)
            .str.strip()
        )

        unidades = unidades[
            ~unidades.str.lower().isin(
                ["", "nan", "none", "nat"]
            )
        ]

        if unidades.empty:

            print(
                f"Atenção: {id_mma_completo} "
                f"não possui unidade informada."
            )

            continue

        unidades_encontradas = unidades.unique()

        if len(unidades_encontradas) > 1:

            print(
                f"Atenção: {id_mma_completo} possui "
                f"mais de uma unidade: "
                f"{list(unidades_encontradas)}"
            )

        unidade_atual = unidades_encontradas[0]

        # ======================================================
        # BUSCA AS CONVERSÕES DO POLUENTE
        # ======================================================

        conversoes = tabela_conversao[
            tabela_conversao["POLUENTE"]
            .astype(str)
            .str.strip()
            .str.upper()
            ==
            poluente.upper()
        ].copy()

        if conversoes.empty:

            print(
                f"Atenção: não existe conversão "
                f"cadastrada para {poluente}."
            )

            continue

        # ======================================================
        # VERIFICA SE JÁ ESTÁ NA UNIDADE DESTINO
        # ======================================================

        unidade_correta = conversoes[
            conversoes["UNIDADE_DESTINO"]
            .astype(str)
            .str.strip()
            .str.lower()
            ==
            unidade_atual.lower()
        ]

        if not unidade_correta.empty:

            print(
                f"{id_mma_completo}: "
                f"{poluente} já está em "
                f"{unidade_atual}."
            )

            df.iloc[:, posicao_unidade] = unidade_atual

            continue

        # ======================================================
        # PROCURA A CONVERSÃO
        # ======================================================

        conversao = conversoes[
            conversoes["UNIDADE_ORIGEM"]
            .astype(str)
            .str.strip()
            .str.lower()
            ==
            unidade_atual.lower()
        ]

        if conversao.empty:

            print(
                f"Atenção: {id_mma_completo} - "
                f"não existe conversão de "
                f"{unidade_atual} para {poluente}."
            )

            continue

        # ======================================================
        # OBTÉM O FATOR
        # ======================================================

        linha_conversao = conversao.iloc[0]

        unidade_destino = str(
            linha_conversao["UNIDADE_DESTINO"]
        ).strip()

        fator = linha_conversao[
            "FATOR_CONVERSAO"
        ]

        if pd.isna(fator) or str(fator).strip() == "":

            print(
                f"Atenção: {id_mma_completo} - "
                f"não existe fator de conversão de "
                f"{unidade_atual} para "
                f"{unidade_destino}."
            )

            continue

        fator = float(fator)

        # ======================================================
        # CONVERTE OS VALORES
        # ======================================================

        valores_originais = (
            df.iloc[:, posicao_valor]
            .astype(str)
            .str.strip()
        )

        valores_numericos = pd.to_numeric(
            valores_originais,
            errors="coerce"
        )

        # Identifica os valores especiais
        mascara_especial = valores_originais.isin(
            valores_especiais
        )

        # Converte somente os valores normais
        valores_convertidos = (
            valores_numericos * fator
        )

        # Mantém os valores especiais exatamente como estavam
        df.iloc[:, posicao_valor] = valores_convertidos

        df.iloc[
            mascara_especial.values,
            posicao_valor
        ] = valores_originais[
            mascara_especial
        ].values

        # ======================================================
        # ATUALIZA A UNIDADE
        # ======================================================

        df.iloc[:, posicao_unidade] = unidade_destino

        # ======================================================
        # RELATÓRIO
        # ======================================================

        quantidade_valores = (
            valores_numericos.notna().sum()
        )

        quantidade_especiais = (
            mascara_especial.sum()
        )

        print(
            f"{id_mma_completo}: "
            f"{poluente} | "
            f"{unidade_atual} → {unidade_destino} | "
            f"Fator: {fator} | "
            f"Valores convertidos: "
            f"{quantidade_valores - quantidade_especiais} | "
            f"Valores especiais mantidos: "
            f"{quantidade_especiais}"
        )

    # ==========================================================
    # SALVA O ARQUIVO
    # ==========================================================

    df.to_csv(
        caminho_arquivo,
        index=False,
        encoding="utf-8",
        sep=","
    )

    print(
        "\n✓ Verificação de unidades concluída!"
    )

    print(
        f"Arquivo atualizado em:\n{caminho_arquivo}"
    )