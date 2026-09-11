
import os
import pandas as pd
from rapidfuzz import fuzz


def comparar_estacoes(
    UF,
    ANO_ANTERIOR,
    ANO_ATUAL,
    base="/home/nobre/Notebooks/RQAr/dados/dados_formatados",
    substituicoes=None
):
    """
    Compara as estações entre dois anos.

    REGRAS DO MATCH
    ---------------

    MATCH = "S"
    -------------
    Só considera match aprovado quando TODOS os critérios forem iguais:

        1. ID_OEMA igual
        2. LATITUDE igual
        3. LONGITUDE igual
        4. POLUENTE igual

    MATCH = "M"
    -------------
    Quando:

        1. ID_OEMA igual
        2. LATITUDE igual
        3. LONGITUDE igual
        4. POLUENTE diferente

    Nesse caso, "M" significa que a estação é a mesma e o
    ID_MMA pode ser aproveitado posteriormente, mas os demais
    dados do poluente NÃO devem ser preenchidos.

    OUTROS CASOS
    ------------
    Não são considerados match.

    IMPORTANTE
    ----------
    Não utiliza similaridade do ID_OEMA para aprovar um match.
    O ID_OEMA precisa ser exatamente igual.

    O arquivo de matches terá as colunas:

        ID_OEMA_2024
        ID_OEMA_2025
        POLUENTE_2024
        POLUENTE_2025
        POLUENTE
        SIMILARIDADE
        LAT_2024
        LAT_2025
        LON_2024
        LON_2025
        LAT_OK
        LON_OK
        APROVADO
        OBSERVACAO

    APROVADO:
        S = estação + poluente correspondentes
        M = mesma estação, mas poluente diferente
    """

    # ==========================================================
    # CONFIGURAÇÃO
    # ==========================================================

    UF = str(UF).upper().strip()

    if substituicoes is None:
        substituicoes = {}

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

    pasta_saida = (
        f"{base}/{ANO_ATUAL}/rede/"
        f"comparando_tabelas/{UF}"
    )

    os.makedirs(
        pasta_saida,
        exist_ok=True
    )

    arquivo_matches = os.path.join(
        pasta_saida,
        f"matches_{UF}_{ANO_ANTERIOR}_{ANO_ATUAL}.csv"
    )

    arquivo_nao = os.path.join(
        pasta_saida,
        f"{UF}_nao_encontrados_"
        f"{ANO_ANTERIOR}_{ANO_ATUAL}.csv"
    )

    # ==========================================================
    # VERIFICAÇÃO DOS ARQUIVOS
    # ==========================================================

    if not os.path.exists(arquivo_anterior):
        raise FileNotFoundError(
            f"Arquivo do ano anterior não encontrado:\n"
            f"{arquivo_anterior}"
        )

    if not os.path.exists(arquivo_atual):
        raise FileNotFoundError(
            f"Arquivo do ano atual não encontrado:\n"
            f"{arquivo_atual}"
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

    # ==========================================================
    # COLUNAS OBRIGATÓRIAS
    # ==========================================================

    colunas_obrigatorias = [
        "ID_OEMA",
        "POLUENTE",
        "LATITUDE",
        "LONGITUDE"
    ]

    for coluna in colunas_obrigatorias:

        if coluna not in df_anterior.columns:
            raise ValueError(
                f"A coluna '{coluna}' não existe no arquivo "
                f"do ano {ANO_ANTERIOR}."
            )

        if coluna not in df_atual.columns:
            raise ValueError(
                f"A coluna '{coluna}' não existe no arquivo "
                f"do ano {ANO_ATUAL}."
            )

    # ==========================================================
    # NORMALIZAÇÃO
    # ==========================================================

    for df in [df_anterior, df_atual]:

        for coluna in [
            "ID_OEMA",
            "POLUENTE",
            "LATITUDE",
            "LONGITUDE"
        ]:

            df[coluna] = (
                df[coluna]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    # ==========================================================
    # FUNÇÕES AUXILIARES
    # ==========================================================

    def valor_preenchido(valor):

        if pd.isna(valor):
            return False

        valor = str(valor).strip().lower()

        return valor not in [
            "",
            "nan",
            "none",
            "null"
        ]

    def coordenada_valida(valor):

        if not valor_preenchido(valor):
            return False

        try:
            float(valor)
            return True

        except (ValueError, TypeError):
            return False

    def coordenadas_iguais(
        lat_1,
        lon_1,
        lat_2,
        lon_2
    ):

        if not (
            coordenada_valida(lat_1)
            and coordenada_valida(lon_1)
            and coordenada_valida(lat_2)
            and coordenada_valida(lon_2)
        ):
            return False

        try:

            return (
                float(lat_1) == float(lat_2)
                and
                float(lon_1) == float(lon_2)
            )

        except (ValueError, TypeError):

            return False

    # ==========================================================
    # MATCH
    # ==========================================================

    matches = []

    # Guarda as combinações do ano anterior que foram
    # efetivamente encontradas
    pares_encontrados = set()

    # ==========================================================
    # LOOP PELO ANO ATUAL
    # ==========================================================

    for _, linha_atual in df_atual.iterrows():

        id_atual = str(
            linha_atual["ID_OEMA"]
        ).strip()

        poluente_atual = str(
            linha_atual["POLUENTE"]
        ).strip()

        lat_atual = linha_atual["LATITUDE"]
        lon_atual = linha_atual["LONGITUDE"]

        # ======================================================
        # PROCURA SOMENTE PELO MESMO ID_OEMA
        # ======================================================

        candidatos = df_anterior[
            df_anterior["ID_OEMA"]
            .eq(id_atual)
        ]

        if candidatos.empty:
            continue

        # ======================================================
        # PROCURA ENTRE AS LINHAS DO MESMO ID_OEMA
        # POR LATITUDE + LONGITUDE
        # ======================================================

        melhor = None

        for _, candidato in candidatos.iterrows():

            lat_anterior = candidato["LATITUDE"]
            lon_anterior = candidato["LONGITUDE"]

            if coordenadas_iguais(
                lat_atual,
                lon_atual,
                lat_anterior,
                lon_anterior
            ):

                melhor = candidato

                break

        # ======================================================
        # SE NÃO ACHOU MESMO ID_OEMA + LAT + LON
        # NÃO É MATCH
        # ======================================================

        if melhor is None:
            continue

        # ======================================================
        # INFORMAÇÕES DO ANO ANTERIOR
        # ======================================================

        id_anterior = str(
            melhor["ID_OEMA"]
        ).strip()

        poluente_anterior = str(
            melhor["POLUENTE"]
        ).strip()

        lat_anterior = melhor["LATITUDE"]
        lon_anterior = melhor["LONGITUDE"]

        # ======================================================
        # VERIFICA LATITUDE
        # ======================================================

        lat_ok = coordenadas_iguais(
            lat_atual,
            lon_atual,
            lat_anterior,
            lon_anterior
        )

        # Aqui a latitude e longitude já foram verificadas juntas.
        # Mantemos as duas colunas separadas no resultado.

        if (
            coordenada_valida(lat_atual)
            and coordenada_valida(lat_anterior)
        ):

            try:

                lat_ok = (
                    float(lat_atual)
                    ==
                    float(lat_anterior)
                )

            except (ValueError, TypeError):

                lat_ok = False

        else:

            lat_ok = False

        # ======================================================
        # VERIFICA LONGITUDE
        # ======================================================

        if (
            coordenada_valida(lon_atual)
            and coordenada_valida(lon_anterior)
        ):

            try:

                lon_ok = (
                    float(lon_atual)
                    ==
                    float(lon_anterior)
                )

            except (ValueError, TypeError):

                lon_ok = False

        else:

            lon_ok = False

        # ======================================================
        # VERIFICA POLUENTE
        # ======================================================

        poluente_igual = (
            poluente_atual
            ==
            poluente_anterior
        )

        # ======================================================
        # DEFINE APROVAÇÃO
        # ======================================================

        if (
            id_atual == id_anterior
            and
            lat_ok
            and
            lon_ok
            and
            poluente_igual
        ):

            aprovado = "S"

            observacao = (
                "MATCH por ID_OEMA + LATITUDE + "
                "LONGITUDE + POLUENTE"
            )

        elif (
            id_atual == id_anterior
            and
            lat_ok
            and
            lon_ok
            and
            not poluente_igual
        ):

            aprovado = "M"

            observacao = (
                "MESMA ESTAÇÃO, POLUENTE diferente; "
                "ID_MMA pode ser aproveitado"
            )

        else:

            # Este caso praticamente não ocorrerá porque
            # o candidato já foi filtrado por ID_OEMA + LAT/LON.
            continue

        # ======================================================
        # SIMILARIDADE DO ID_OEMA
        # ======================================================

        similaridade = fuzz.ratio(
            id_atual,
            id_anterior
        )

        # ======================================================
        # ADICIONA AO MATCH
        # ======================================================

        matches.append({

            f"ID_OEMA_{ANO_ANTERIOR}":
                id_anterior,

            f"ID_OEMA_{ANO_ATUAL}":
                id_atual,

            f"POLUENTE_{ANO_ANTERIOR}":
                poluente_anterior,

            f"POLUENTE_{ANO_ATUAL}":
                poluente_atual,

            # Mantém POLUENTE para compatibilidade
            # com sua função posterior
            "POLUENTE":
                poluente_atual,

            "SIMILARIDADE":
                round(similaridade, 1),

            f"LAT_{ANO_ANTERIOR}":
                lat_anterior,

            f"LAT_{ANO_ATUAL}":
                lat_atual,

            f"LON_{ANO_ANTERIOR}":
                lon_anterior,

            f"LON_{ANO_ATUAL}":
                lon_atual,

            "LAT_OK":
                lat_ok,

            "LON_OK":
                lon_ok,

            "APROVADO":
                aprovado,

            "OBSERVACAO":
                observacao
        })

        # ======================================================
        # MARCA O PAR DO ANO ANTERIOR COMO ENCONTRADO
        # ======================================================

        pares_encontrados.add(
            (
                id_anterior,
                poluente_anterior
            )
        )

    # ==========================================================
    # DATAFRAME DE MATCHES
    # ==========================================================

    colunas_saida = [
        f"ID_OEMA_{ANO_ANTERIOR}",
        f"ID_OEMA_{ANO_ATUAL}",
        f"POLUENTE_{ANO_ANTERIOR}",
        f"POLUENTE_{ANO_ATUAL}",
        "POLUENTE",
        "SIMILARIDADE",
        f"LAT_{ANO_ANTERIOR}",
        f"LAT_{ANO_ATUAL}",
        f"LON_{ANO_ANTERIOR}",
        f"LON_{ANO_ATUAL}",
        "LAT_OK",
        "LON_OK",
        "APROVADO",
        "OBSERVACAO"
    ]

    df_matches = pd.DataFrame(
        matches,
        columns=colunas_saida
    )

    # ==========================================================
    # NÃO ENCONTRADOS DO ANO ANTERIOR
    # ==========================================================

    nao_anterior = []

    for _, linha_anterior in df_anterior.iterrows():

        chave = (
            linha_anterior["ID_OEMA"],
            linha_anterior["POLUENTE"]
        )

        if chave not in pares_encontrados:

            nao_anterior.append({

                f"ID_OEMA_{ANO_ANTERIOR}":
                    linha_anterior["ID_OEMA"],

                f"POLUENTE_{ANO_ANTERIOR}":
                    linha_anterior["POLUENTE"]
            })

    # ==========================================================
    # NÃO ENCONTRADOS DO ANO ATUAL
    # ==========================================================

    pares_atual = set()

    if not df_matches.empty:

        pares_atual = set(
            zip(
                df_matches[
                    f"ID_OEMA_{ANO_ATUAL}"
                ],

                df_matches[
                    f"POLUENTE_{ANO_ATUAL}"
                ]
            )
        )

    nao_atual = []

    for _, linha_atual in df_atual.iterrows():

        chave = (
            linha_atual["ID_OEMA"],
            linha_atual["POLUENTE"]
        )

        if chave not in pares_atual:

            nao_atual.append({

                f"ID_OEMA_{ANO_ATUAL}":
                    linha_atual["ID_OEMA"],

                "POLUENTE":
                    linha_atual["POLUENTE"]
            })

    # ==========================================================
    # DATAFRAME NÃO ENCONTRADOS
    # ==========================================================

    df_nao_atual = pd.DataFrame(
        nao_atual
    )

    df_nao_anterior = pd.DataFrame(
        nao_anterior
    )

    df_nao = pd.concat(
        [
            df_nao_atual.reset_index(
                drop=True
            ),

            df_nao_anterior.reset_index(
                drop=True
            )
        ],
        axis=1
    )

    # ==========================================================
    # SALVA MATCHES
    # ==========================================================

    df_matches.to_csv(
        arquivo_matches,
        index=False,
        encoding="utf-8-sig"
    )

    # ==========================================================
    # SALVA NÃO ENCONTRADOS
    # ==========================================================

    df_nao.to_csv(
        arquivo_nao,
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
        "COMPARAÇÃO CONCLUÍDA!"
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
        f"\nTotal de matches: "
        f"{len(df_matches)}"
    )

    if not df_matches.empty:

        quantidade_s = (
            df_matches["APROVADO"]
            .eq("S")
            .sum()
        )

        quantidade_m = (
            df_matches["APROVADO"]
            .eq("M")
            .sum()
        )

    else:

        quantidade_s = 0
        quantidade_m = 0

    print(
        f"Matches S: "
        f"{quantidade_s}"
    )

    print(
        f"Matches M: "
        f"{quantidade_m}"
    )

    print(
        f"Não encontrados: "
        f"{len(df_nao)}"
    )

    print(
        "\n------------------------------------------"
    )

    print(
        "S = ID_OEMA + LAT/LON + POLUENTE iguais"
    )

    print(
        "M = ID_OEMA + LAT/LON iguais, "
        "mas POLUENTE diferente"
    )

    print(
        "------------------------------------------"
    )

    print(
        f"Arquivo de matches:\n"
        f"{arquivo_matches}"
    )

    print(
        f"\nArquivo de não encontrados:\n"
        f"{arquivo_nao}"
    )

    print(
        "=========================================="
    )

    return df_matches, df_nao

