import os
import pandas as pd

from funcoes_monitoramento.corrige_datetime_MQAr import (
    corrige_datetime_MQAr
)


def atualiza_series_MQAr_QAQC(
    caminho_arquivo,
    ano,
    uf
):

    caminho_rede = (
        f"/home/nobre/Notebooks/RQAr/dados/dados_formatados/"
        f"{ano}/rede/{uf}_Rede_{ano}.csv"
    )

    pasta_MQAr = (
        f"/home/nobre/Notebooks/RQAr/dados/MQAr_{ano}"
    )

    # ==========================================================
    # 1. LEITURA DOS ARQUIVOS
    # ==========================================================

    df = pd.read_csv(
        caminho_arquivo,
        dtype=str
    )

    df_rede = pd.read_csv(
        caminho_rede,
        dtype=str
    )

    # Limpa espaços dos nomes das colunas
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    df_rede.columns = (
        df_rede.columns
        .astype(str)
        .str.strip()
    )

    # ==========================================================
    # 2. COLUNAS OBRIGATÓRIAS
    # ==========================================================

    colunas_base = [
        "DATETIME",
        "ANO",
        "MES",
        "DIA",
        "HORA"
    ]

    for coluna in colunas_base:

        if coluna not in df.columns:

            raise ValueError(
                f"A coluna '{coluna}' não existe "
                f"no arquivo atual."
            )

    if "ID_MMA_COMPLETO" not in df_rede.columns:

        raise ValueError(
            "A coluna 'ID_MMA_COMPLETO' não existe "
            "na tabela de rede."
        )

    if "POLUENTE" not in df_rede.columns:

        raise ValueError(
            "A coluna 'POLUENTE' não existe "
            "na tabela de rede."
        )

    # ==========================================================
    # 3. CONVERTE DATETIME DO ARQUIVO ATUAL
    # ==========================================================

    df["DATETIME"] = pd.to_datetime(
        df["DATETIME"],
        errors="coerce"
    )

    quantidade_invalidos = (
        df["DATETIME"].isna().sum()
    )

    if quantidade_invalidos > 0:

        raise ValueError(
            f"Foram encontrados {quantidade_invalidos} "
            f"valores inválidos na coluna DATETIME "
            f"do arquivo intermediário."
        )

    # ==========================================================
    # 4. IDENTIFICA AS ESTAÇÕES
    # ==========================================================

    colunas_estacoes = []

    for coluna in df.columns:

        # Ignora as colunas gerais
        if coluna in colunas_base:
            continue

        # Ignora colunas de unidade
        if coluna.startswith("UNIDADE_"):
            continue

        # Ignora colunas de QAQC
        if coluna.startswith("QAQC_"):
            continue

        # O que sobrou é considerado ID_MMA_COMPLETO
        colunas_estacoes.append(coluna)

    print(
        f"Estações encontradas no arquivo: "
        f"{len(colunas_estacoes)}"
    )

    # ==========================================================
    # 5. PROCESSA CADA ESTAÇÃO
    # ==========================================================

    for id_mma in colunas_estacoes:

        id_mma = str(id_mma).strip()

        print("\n" + "=" * 60)
        print(f"Processando: {id_mma}")

        # ======================================================
        # 5.1 PROCURA O ID NA TABELA DE REDE
        # ======================================================

        registro_rede = df_rede[
            df_rede["ID_MMA_COMPLETO"]
            .astype(str)
            .str.strip()
            == id_mma
        ]

        if registro_rede.empty:

            raise ValueError(
                f"{id_mma} não foi encontrado "
                f"na tabela de rede."
            )

        # ======================================================
        # 5.2 OBTÉM O POLUENTE
        # ======================================================

        poluente = registro_rede.iloc[0]["POLUENTE"]

        if pd.isna(poluente) or str(poluente).strip() == "":

            raise ValueError(
                f"Não foi encontrado POLUENTE para "
                f"{id_mma} na tabela de rede."
            )

        poluente = str(poluente).strip()

        print(
            f"Poluente encontrado: {poluente}"
        )

        # ======================================================
        # 6. IDENTIFICA AS TRÊS COLUNAS DA ESTAÇÃO
        # ======================================================

        coluna_valor = id_mma

        coluna_unidade = (
            f"UNIDADE_{id_mma}"
        )

        # NOVO PADRÃO:
        # QAQC_ID_MMA_COMPLETO
        coluna_qaqc = (
            f"QAQC_{id_mma}"
        )

        # ------------------------------------------------------
        # Verifica se as três existem
        # ------------------------------------------------------

        if coluna_valor not in df.columns:

            raise ValueError(
                f"A coluna '{coluna_valor}' "
                f"não existe no arquivo."
            )

        if coluna_unidade not in df.columns:

            raise ValueError(
                f"A coluna '{coluna_unidade}' "
                f"não existe no arquivo."
            )

        if coluna_qaqc not in df.columns:

            raise ValueError(
                f"A coluna '{coluna_qaqc}' "
                f"não existe no arquivo."
            )

        # ======================================================
        # 7. VERIFICA A PASTA DO POLUENTE
        # ======================================================

        pasta_poluente = os.path.join(
            pasta_MQAr,
            poluente
        )

        if not os.path.isdir(pasta_poluente):

            raise FileNotFoundError(
                f"A pasta do poluente '{poluente}' "
                f"não existe: {pasta_poluente}"
            )

        # ======================================================
        # 8. DEFINE O ARQUIVO DE DESTINO
        # ======================================================

        caminho_saida = os.path.join(
            pasta_poluente,
            f"{id_mma}.csv"
        )

        print(
            f"Arquivo de destino: {caminho_saida}"
        )

        # ======================================================
        # 9. SELECIONA OS DADOS DA ESTAÇÃO
        # ======================================================

        dados_novos = pd.DataFrame()

        dados_novos["DATETIME"] = (
            df["DATETIME"]
        )

        dados_novos["VALOR"] = pd.to_numeric(
            df[coluna_valor],
            errors="coerce"
        )

        dados_novos["UNIDADE"] = (
            df[coluna_unidade]
        )

        dados_novos["QAQC_INTERNO"] = (
            df[coluna_qaqc]
        )

        dados_novos = dados_novos.sort_values(
            "DATETIME"
        ).reset_index(drop=True)

        # ======================================================
        # 10. VERIFICA DATETIME DUPLICADO NOS DADOS NOVOS
        # ======================================================

        duplicados_novos = dados_novos[
            dados_novos["DATETIME"].duplicated(
                keep=False
            )
        ]

        if not duplicados_novos.empty:

            horarios_duplicados = (
                duplicados_novos["DATETIME"]
                .dt.strftime("%Y-%m-%d %H:%M:%S")
                .unique()
                .tolist()
            )

            raise ValueError(
                f"Foram encontrados DATETIME duplicados "
                f"para {id_mma} no arquivo intermediário: "
                f"{horarios_duplicados}"
            )

        # ======================================================
        # 11. ARQUIVO JÁ EXISTE
        # ======================================================

        if os.path.isfile(caminho_saida):

            print(
                "Arquivo existente encontrado."
            )

            df_existente = pd.read_csv(
                caminho_saida,
                dtype=str
            )

            df_existente.columns = (
                df_existente.columns
                .astype(str)
                .str.strip()
            )

            if "DATETIME" not in df_existente.columns:

                raise ValueError(
                    f"O arquivo {caminho_saida} "
                    f"não possui a coluna DATETIME."
                )

            # --------------------------------------------------
            # 11.1 Converte DATETIME existente
            # --------------------------------------------------

            df_existente["DATETIME"] = pd.to_datetime(
                df_existente["DATETIME"],
                errors="coerce"
            )

            quantidade_invalidos = (
                df_existente["DATETIME"].isna().sum()
            )

            datetime_corrigido = False

            if quantidade_invalidos > 0:

                print(
                    f"ATENÇÃO: o arquivo possui "
                    f"{quantidade_invalidos} "
                    f"DATETIME inválido(s)."
                )

                df_existente = corrige_datetime_MQAr(
                    df_existente,
                    nome_arquivo=caminho_saida
                )

                datetime_corrigido = True

            # --------------------------------------------------
            # 11.2 Verifica duplicidades
            # --------------------------------------------------

            duplicados_existentes = df_existente[
                df_existente["DATETIME"].duplicated(
                    keep=False
                )
            ]

            if not duplicados_existentes.empty:

                horarios_duplicados = (
                    duplicados_existentes["DATETIME"]
                    .dt.strftime("%Y-%m-%d %H:%M:%S")
                    .unique()
                    .tolist()
                )

                raise ValueError(
                    f"Foram encontrados DATETIME duplicados "
                    f"no arquivo existente "
                    f"{caminho_saida}: "
                    f"{horarios_duplicados}"
                )

            # --------------------------------------------------
            # 11.3 Ordena histórico
            # --------------------------------------------------

            df_existente = df_existente.sort_values(
                "DATETIME"
            ).reset_index(drop=True)

            # --------------------------------------------------
            # 11.4 Último horário existente
            # --------------------------------------------------

            ultimo_datetime = (
                df_existente["DATETIME"].max()
            )

            # ==================================================
            # 12. SELECIONA SOMENTE OS DADOS POSTERIORES
            # ==================================================

            dados_para_adicionar = dados_novos[
                dados_novos["DATETIME"] > ultimo_datetime
            ].copy()

            # ==================================================
            # 13. NÃO EXISTEM DADOS NOVOS
            # ==================================================

            if dados_para_adicionar.empty:

                if datetime_corrigido:

                    print(
                        "Nenhum dado novo encontrado."
                    )

                    print(
                        "→ Salvando apenas a correção "
                        "do DATETIME."
                    )

                    df_final = df_existente

                else:

                    print(
                        f"Nenhum dado novo para {id_mma}."
                    )

                    continue

            else:

                # ==================================================
                # 14. IDENTIFICA LACUNA HORÁRIA
                # ==================================================

                primeiro_datetime_novo = (
                    dados_para_adicionar["DATETIME"].min()
                )

                inicio_lacuna = (
                    ultimo_datetime
                    + pd.Timedelta(hours=1)
                )

                fim_lacuna = (
                    primeiro_datetime_novo
                    - pd.Timedelta(hours=1)
                )

                lacunas = pd.DataFrame(
                    columns=[
                        "DATETIME",
                        "VALOR",
                        "UNIDADE",
                        "QAQC_INTERNO"
                    ]
                )

                if inicio_lacuna <= fim_lacuna:

                    horarios_lacuna = pd.date_range(
                        start=inicio_lacuna,
                        end=fim_lacuna,
                        freq="h"
                    )

                    # ==================================================
                    # CORREÇÃO DO FutureWarning
                    # ==================================================

                    lacunas = pd.DataFrame({
                        "DATETIME": horarios_lacuna,
                        "VALOR": pd.Series(
                            [pd.NA] * len(horarios_lacuna),
                            dtype="object"
                        ),
                        "UNIDADE": pd.Series(
                            [pd.NA] * len(horarios_lacuna),
                            dtype="object"
                        ),
                        "QAQC_INTERNO": pd.Series(
                            [pd.NA] * len(horarios_lacuna),
                            dtype="object"
                        )
                    })

                    print(
                        f"Lacuna encontrada: "
                        f"{ultimo_datetime} → "
                        f"{primeiro_datetime_novo}"
                    )

                    print(
                        f"→ {len(lacunas)} horário(s) "
                        f"preenchido(s) com dados vazios."
                    )

                # ==================================================
                # 15. JUNTA LACUNAS + DADOS NOVOS
                # ==================================================

                dados_entrada = pd.concat(
                    [
                        lacunas,
                        dados_para_adicionar
                    ],
                    ignore_index=True
                )

                # ==================================================
                # 16. CRIA NOVAS LINHAS
                # ==================================================

                novas_linhas = pd.DataFrame()

                novas_linhas["DATETIME"] = (
                    dados_entrada["DATETIME"]
                )

                novas_linhas["ANO"] = (
                    dados_entrada["DATETIME"].dt.year
                )

                novas_linhas["MES"] = (
                    dados_entrada["DATETIME"].dt.month
                )

                novas_linhas["DIA"] = (
                    dados_entrada["DATETIME"].dt.day
                )

                novas_linhas["HORA"] = (
                    dados_entrada["DATETIME"].dt.hour
                )

                novas_linhas["VALOR"] = (
                    dados_entrada["VALOR"]
                )

                # ==================================================
                # CORREÇÃO DO FutureWarning
                # ==================================================

                novas_linhas["VALOR_ORIGINAL"] = pd.Series(
                    [pd.NA] * len(novas_linhas),
                    dtype="object"
                )

                novas_linhas["UNIDADE"] = (
                    dados_entrada["UNIDADE"]
                )

                novas_linhas["QAQC_INTERNO"] = (
                    dados_entrada["QAQC_INTERNO"]
                )

                novas_linhas["QAQC_MMA"] = pd.Series(
                    [pd.NA] * len(novas_linhas),
                    dtype="object"
                )

                # ==================================================
                # 17. GARANTE PADRÃO DO ARQUIVO EXISTENTE
                # ==================================================

                colunas_finais = [
                    "DATETIME",
                    "ANO",
                    "MES",
                    "DIA",
                    "HORA",
                    "VALOR",
                    "VALOR_ORIGINAL",
                    "UNIDADE",
                    "QAQC_INTERNO",
                    "QAQC_MMA"
                ]

                for coluna in colunas_finais:

                    if coluna not in df_existente.columns:

                        df_existente[coluna] = pd.NA

                df_existente = df_existente[
                    colunas_finais
                ]

                novas_linhas = novas_linhas[
                    colunas_finais
                ]

                # ==================================================
                # 18. JUNTA HISTÓRICO + ATUALIZAÇÃO
                # ==================================================

                df_final = pd.concat(
                    [
                        df_existente,
                        novas_linhas
                    ],
                    ignore_index=True
                )

                print(
                    f"Novos registros adicionados: "
                    f"{len(dados_para_adicionar)}"
                )

        # ======================================================
        # 19. ARQUIVO NÃO EXISTE
        # ======================================================

        elif not os.path.exists(caminho_saida):

            print(
                "Arquivo da estação não encontrado."
            )

            print(
                "→ Criando novo arquivo."
            )

            df_final = pd.DataFrame()

            df_final["DATETIME"] = (
                dados_novos["DATETIME"]
            )

            df_final["ANO"] = (
                dados_novos["DATETIME"].dt.year
            )

            df_final["MES"] = (
                dados_novos["DATETIME"].dt.month
            )

            df_final["DIA"] = (
                dados_novos["DATETIME"].dt.day
            )

            df_final["HORA"] = (
                dados_novos["DATETIME"].dt.hour
            )

            df_final["VALOR"] = (
                dados_novos["VALOR"]
            )

            df_final["VALOR_ORIGINAL"] = pd.Series(
                [pd.NA] * len(df_final),
                dtype="object"
            )

            df_final["UNIDADE"] = (
                dados_novos["UNIDADE"]
            )

            df_final["QAQC_INTERNO"] = (
                dados_novos["QAQC_INTERNO"]
            )

            df_final["QAQC_MMA"] = pd.Series(
                [pd.NA] * len(df_final),
                dtype="object"
            )

        else:

            raise ValueError(
                f"O caminho de destino existe, mas não é "
                f"um arquivo CSV válido: {caminho_saida}"
            )

        # ======================================================
        # 20. VERIFICA DUPLICIDADES NO RESULTADO FINAL
        # ======================================================

        duplicados_finais = df_final[
            df_final["DATETIME"].duplicated(
                keep=False
            )
        ]

        if not duplicados_finais.empty:

            horarios_duplicados = (
                duplicados_finais["DATETIME"]
                .dt.strftime("%Y-%m-%d %H:%M:%S")
                .unique()
                .tolist()
            )

            raise ValueError(
                f"Foram encontrados DATETIME duplicados "
                f"no resultado final de {id_mma}: "
                f"{horarios_duplicados}"
            )

        # ======================================================
        # 21. ORDENAÇÃO FINAL
        # ======================================================

        df_final = df_final.sort_values(
            "DATETIME"
        ).reset_index(drop=True)

        # ======================================================
        # 22. RECRIA ANO, MES, DIA E HORA
        # ======================================================

        df_final["ANO"] = (
            df_final["DATETIME"].dt.year
        )

        df_final["MES"] = (
            df_final["DATETIME"].dt.month
        )

        df_final["DIA"] = (
            df_final["DATETIME"].dt.day
        )

        df_final["HORA"] = (
            df_final["DATETIME"].dt.hour
        )

        # ======================================================
        # 23. FORMATA DATETIME
        # ======================================================

        df_final["DATETIME"] = (
            df_final["DATETIME"]
            .dt.strftime("%Y-%m-%d %H:%M:%S")
        )

        # ======================================================
        # 24. GARANTE ORDEM DAS COLUNAS
        # ======================================================

        df_final = df_final[
            [
                "DATETIME",
                "ANO",
                "MES",
                "DIA",
                "HORA",
                "VALOR",
                "VALOR_ORIGINAL",
                "UNIDADE",
                "QAQC_INTERNO",
                "QAQC_MMA"
            ]
        ]

        # ======================================================
        # 25. SALVA
        # ======================================================

        df_final.to_csv(
            caminho_saida,
            index=False,
            encoding="utf-8",
            sep=","
        )

        print(
            f"✓ {id_mma} atualizado com sucesso."
        )

    print(
        "\nProcessamento concluído."
    )