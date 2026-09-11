import pandas as pd

def preencher_dados_monitoramento(
    uf,
    caminho_base="/home/nobre/Notebooks/RQAr/dados/Monitoramento_QAr_BR_2025.csv",
    pasta_rede="/home/nobre/Notebooks/RQAr/dados/dados_formatados/2025/rede",
):
    """
    Preenche informações faltantes da planilha da rede utilizando
    a base nacional Monitoramento_QAr_BR_2025.csv.

    Origem dos dados:
        caminho_base

    Arquivo preenchido:
        pasta_rede/{UF}_Rede_2025.csv

    Match das informações:
        UF
        ID_MMA
        COD_POLUENTE

    Prioridade:
        - Mantém sempre os valores já existentes na planilha da rede.
        - Preenche apenas campos vazios.

    Não preenche:
        INICIO
        FIM
        ELEVACAO
        BASE_DADOS
        ANOS_MONITORADOS

    Não copia:
        Nao Declarado
        Não Declarado

    Também mostra no terminal os registros da rede que não
    encontraram correspondência na base nacional, diferenciando:
        1. ID_MMA não encontrado na base.
        2. ID_MMA encontrado, mas COD_POLUENTE diferente.

    A coluna COD_POLUENTE é padronizada para três dígitos.
    Valores como 1, 01, 001 e 1.0 são tratados como 001.
    """

    caminho_rede = f"{pasta_rede}/{uf}_Rede_2025.csv"

    def padronizar_cod_poluente(valor):
        if pd.isna(valor):
            return ""
        valor = str(valor).strip()
        if valor == "":
            return ""
        try:
            numero = float(valor)
            if numero.is_integer():
                return str(int(numero)).zfill(3)
        except (ValueError, TypeError):
            pass
        return valor

    # LEITURA
    df_base = pd.read_csv(caminho_base, dtype=str)
    df_rede = pd.read_csv(caminho_rede, dtype=str)

    # VERIFICAÇÃO DAS COLUNAS
    chaves = ["UF", "ID_MMA", "COD_POLUENTE"]

    for coluna in chaves:
        if coluna not in df_base.columns:
            raise ValueError(
                f"A coluna '{coluna}' não existe na base nacional."
            )
        if coluna not in df_rede.columns:
            raise ValueError(
                f"A coluna '{coluna}' não existe na rede."
            )

    # PADRONIZAÇÃO DAS CHAVES
    for df in [df_base, df_rede]:
        df["UF"] = (
            df["UF"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
        )
        df["ID_MMA"] = (
            df["ID_MMA"]
            .fillna("")
            .astype(str)
            .str.strip()
        )
        df["COD_POLUENTE"] = df["COD_POLUENTE"].apply(
            padronizar_cod_poluente
        )

    # FILTRA A UF
    uf = str(uf).strip().upper()
    df_base = df_base[df_base["UF"] == uf].copy()

    # COLUNAS QUE NÃO DEVEM SER PREENCHIDAS
    colunas_ignorar = [
        "UF",
        "ID_MMA",
        "COD_POLUENTE",
        "INICIO",
        "FIM",
        "ELEVACAO",
        "BASE_DADOS",
        "ANOS_MONITORADOS",
    ]

    # COLUNAS QUE PODEM SER PREENCHIDAS
    colunas_preencher = [
        col for col in df_base.columns
        if col in df_rede.columns and col not in colunas_ignorar
    ]

    print("\nColunas que serão preenchidas:")
    print(colunas_preencher)

    # EVITA DUPLICAÇÃO DA BASE
    df_base_match = (
        df_base[chaves + colunas_preencher]
        .drop_duplicates(subset=chaves, keep="first")
        .copy()
    )

    # DIAGNÓSTICO DOS REGISTROS SEM MATCH
    chaves_base = set(
        zip(
            df_base_match["UF"],
            df_base_match["ID_MMA"],
            df_base_match["COD_POLUENTE"]
        )
    )

    print("\n======================================")
    print("REGISTROS SEM MATCH")
    print("======================================")

    total_nao_encontrados = 0
    total_cod_diferente = 0
    total_id_nao_encontrado = 0

    for _, linha in df_rede.iterrows():
        chave = (
            linha["UF"],
            linha["ID_MMA"],
            linha["COD_POLUENTE"]
        )

        if chave in chaves_base:
            continue

        total_nao_encontrados += 1

        mesmo_id = df_base[
            (df_base["UF"] == linha["UF"]) &
            (df_base["ID_MMA"] == linha["ID_MMA"])
        ]

        if not mesmo_id.empty:
            total_cod_diferente += 1

            codigos_base = sorted(
                mesmo_id["COD_POLUENTE"]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()
            )

            print(
                f"ID_MMA encontrado, mas COD_POLUENTE diferente -> "
                f"POLUENTE={linha.get('POLUENTE', '')} | "
                f"ID_MMA={linha['ID_MMA']} | "
                f"COD_POLUENTE_REDE={linha['COD_POLUENTE']} | "
                f"COD_POLUENTE_BASE={codigos_base}"
            )
        else:
            total_id_nao_encontrado += 1

            print(
                f"Não encontrado -> "
                f"POLUENTE={linha.get('POLUENTE', '')} | "
                f"ID_MMA={linha['ID_MMA']} | "
                f"COD_POLUENTE={linha['COD_POLUENTE']}"
            )

    print("\n--------------------------------------")
    print(f"Total sem match: {total_nao_encontrados}")
    print(f"ID_MMA encontrado, COD diferente: {total_cod_diferente}")
    print(f"ID_MMA não encontrado: {total_id_nao_encontrado}")
    print("--------------------------------------")

    # MERGE
    df = df_rede.merge(
        df_base_match,
        on=chaves,
        how="left",
        suffixes=("", "_BASE"),
    )

    # PREENCHIMENTO
    total_preenchidos = 0

    for coluna in colunas_preencher:
        origem = f"{coluna}_BASE"

        if origem not in df.columns:
            continue

        mascara_destino = (
            df[coluna].isna()
            |
            df[coluna].astype(str).str.strip().eq("")
            |
            df[coluna].astype(str).str.strip().str.lower().isin(
                ["nan", "none"]
            )
        )

        mascara_origem = (
            df[origem].notna()
            &
            df[origem].astype(str).str.strip().ne("")
            &
            ~df[origem].astype(str).str.strip().str.lower().isin(
                ["nao declarado", "não declarado"]
            )
        )

        mascara = mascara_destino & mascara_origem
        quantidade = mascara.sum()

        if quantidade > 0:
            df.loc[mascara, coluna] = df.loc[mascara, origem]
            total_preenchidos += quantidade

        df.drop(columns=origem, inplace=True)

    # RESTAURA VALORES VAZIOS
    df = df.fillna("")

    # SALVA NO MESMO ARQUIVO DA REDE
    df.to_csv(
        caminho_rede,
        index=False,
        encoding="utf-8"
    )

    # RESUMO
    print("\n======================================")
    print("Arquivo atualizado com sucesso!")
    print(f"UF: {uf}")
    print(f"Arquivo: {caminho_rede}")
    print(f"Total de valores preenchidos: {total_preenchidos}")
    print(f"Total sem match: {total_nao_encontrados}")
    print(f"ID_MMA encontrado, COD diferente: {total_cod_diferente}")
    print(f"ID_MMA não encontrado: {total_id_nao_encontrado}")
    print("======================================")