import pandas as pd
import numpy as np


def transforma_15min_QAQC(
    caminho_arquivo,
    caminho_dicionario
):

    # ==========================================================
    # 1. LÊ OS ARQUIVOS
    # ==========================================================

    df = pd.read_csv(
        caminho_arquivo,
        dtype=str
    )

    dicionario = pd.read_csv(
        caminho_dicionario,
        dtype=str
    )

    # ==========================================================
    # 2. IDENTIFICA FLAGS VÁLIDAS
    # ==========================================================

    dicionario["VALIDO"] = (
        dicionario["VALIDO"]
        .str.strip()
        .str.upper()
        .map({
            "TRUE": True,
            "FALSE": False
        })
    )

    flags_validas = dicionario.loc[
        dicionario["VALIDO"] == True,
        "FLAG_QAQC_INTERNO"
    ].tolist()

    # ==========================================================
    # 3. DATETIME
    # ==========================================================

    df["DATETIME"] = pd.to_datetime(
        df["DATETIME"]
    )

    # Volta 15 minutos
    df["DATETIME"] = (
        df["DATETIME"]
        - pd.Timedelta(minutes=15)
    )

    # Define a hora de referência
    df["DATETIME_HORA"] = (
        df["DATETIME"]
        .dt.floor("h")
    )

    # ==========================================================
    # 4. IDENTIFICA COLUNAS QAQC
    # ==========================================================

    colunas_qaqc = [
        coluna
        for coluna in df.columns
        if coluna.startswith("QAQC_")
    ]

    # ==========================================================
    # 5. CRIA RESULTADO COM AS HORAS
    # ==========================================================

    resultado = pd.DataFrame({
        "DATETIME": (
            df["DATETIME_HORA"]
            .drop_duplicates()
            .sort_values()
            .reset_index(drop=True)
        )
    })

    # ==========================================================
    # 6. PROCESSA CADA ESTAÇÃO
    # ==========================================================

    for coluna_qaqc in colunas_qaqc:

        estacao = coluna_qaqc.replace(
            "QAQC_",
            ""
        )

        # ------------------------------------------------------
        # Valores numéricos
        # ------------------------------------------------------

        valores = pd.to_numeric(
            df[estacao],
            errors="coerce"
        )

        # ------------------------------------------------------
        # Identifica medições válidas
        # ------------------------------------------------------

        mascara_valida = (
            df[coluna_qaqc]
            .isin(flags_validas)
        )

        # ------------------------------------------------------
        # Quantidade de válidas por hora
        # ------------------------------------------------------

        qtd_validas = (
            mascara_valida
            .groupby(df["DATETIME_HORA"])
            .sum()
        )

        # ------------------------------------------------------
        # Média somente das válidas
        # ------------------------------------------------------

        media = (
            valores
            .where(mascara_valida)
            .groupby(df["DATETIME_HORA"])
            .mean()
        )

        # ------------------------------------------------------
        # Cria horário
        # ------------------------------------------------------

        horario = pd.DataFrame({
            estacao: media,
            "QTD_VALIDAS": qtd_validas
        })

        # ------------------------------------------------------
        # Se tiver pelo menos 1 válida, mantém o valor.
        #
        # 4 válidas → média
        # 3 válidas → média
        # 2 válidas → média
        # 1 válida  → próprio valor
        # 0 válidas → NaN
        # ------------------------------------------------------

        horario[estacao] = (
            horario[estacao]
            .where(
                horario["QTD_VALIDAS"] >= 1,
                np.nan
            )
        )

        # ------------------------------------------------------
        # QAQC horário
        #
        # 3 ou 4 válidas → TRUE
        # 1 ou 2 válidas → FALSE
        # 0 válidas → FALSE
        # ------------------------------------------------------

        horario[coluna_qaqc] = (
            horario["QTD_VALIDAS"] >= 3
        )

        # ------------------------------------------------------
        # Ajusta índice
        # ------------------------------------------------------

        horario = (
            horario
            .reset_index()
            .rename(
                columns={
                    "DATETIME_HORA": "DATETIME"
                }
            )
        )

        # ------------------------------------------------------
        # Junta ao resultado
        # ------------------------------------------------------

        resultado = resultado.merge(
            horario[
                [
                    "DATETIME",
                    estacao,
                    coluna_qaqc
                ]
            ],
            on="DATETIME",
            how="left"
        )

        # ======================================================
        # 7. MANTÉM UNIDADE
        # ======================================================

        coluna_unidade = (
            f"UNIDADE_{estacao}"
        )

        if coluna_unidade in df.columns:

            unidades = (
                df[coluna_unidade]
                .dropna()
                .astype(str)
                .str.strip()
            )

            if not unidades.empty:

                resultado[coluna_unidade] = (
                    unidades.iloc[0]
                )

    # ==========================================================
    # 8. ORGANIZA AS COLUNAS
    # ==========================================================

    colunas_finais = ["DATETIME"]

    for coluna_qaqc in colunas_qaqc:

        estacao = coluna_qaqc.replace(
            "QAQC_",
            ""
        )

        unidade = (
            f"UNIDADE_{estacao}"
        )

        colunas_finais.append(
            estacao
        )

        if unidade in resultado.columns:

            colunas_finais.append(
                unidade
            )

        colunas_finais.append(
            coluna_qaqc
        )

    resultado = resultado[
        colunas_finais
    ]

    # ==========================================================
    # 9. SALVA
    # ==========================================================

    resultado.to_csv(
        caminho_arquivo,
        index=False
    )

    print(
        "Transformação de 15 minutos para horário "
        "realizada com sucesso!"
    )

    print(
        f"Arquivo atualizado em:\n"
        f"{caminho_arquivo}"
    )

    return resultado