import os
import pandas as pd


def copia_ID_MMA_COMPLETO_MQAr(
    UF,
    pasta_rede="/home/nobre/Notebooks/RQAr/dados/dados_formatados/2025/rede",
    pasta_mqar="/home/nobre/Notebooks/RQAr/dados/MQAr_2025",
):
    """
    Preenche a coluna ID_MMA_COMPLETO utilizando os arquivos da pasta MQAr_2025.

    Lógica:
    -------
    Para cada linha onde ID_MMA_COMPLETO estiver vazio:

    1. Lê o POLUENTE da linha;
    2. Entra na pasta correspondente em MQAr_2025;
    3. Procura um arquivo cujo:
          - ID_MMA = 2 letras + 4 números (6 primeiros caracteres)
          - COD_POLUENTE = 3 últimos caracteres
    4. Quando encontrar, grava o nome do arquivo SEM a extensão ".csv"
       na coluna ID_MMA_COMPLETO.
    """

    arquivo_csv = os.path.join(
        pasta_rede,
        f"{UF}_Rede_2025.csv"
    )

    df = pd.read_csv(arquivo_csv)

    # ---------------------------------------------------------
    # Garantir strings
    # ---------------------------------------------------------
    colunas = ["ID_MMA", "COD_POLUENTE", "POLUENTE", "ID_MMA_COMPLETO"]

    for col in colunas:
        if col not in df.columns:
            raise ValueError(f"Coluna '{col}' não encontrada.")

        df[col] = df[col].fillna("").astype(str).str.strip()

    # COD_POLUENTE sempre com 3 dígitos
    df["COD_POLUENTE"] = (
        pd.to_numeric(df["COD_POLUENTE"], errors="coerce")
        .fillna(0)
        .astype(int)
        .astype(str)
        .str.zfill(3)
    )

    preenchidos = 0

    # =========================================================
    # Percorre linha por linha
    # =========================================================
    for i, row in df.iterrows():

        # Já possui ID_MMA_COMPLETO
        if row["ID_MMA_COMPLETO"] != "":
            continue

        poluente = row["POLUENTE"]
        id_mma = row["ID_MMA"]
        cod = row["COD_POLUENTE"]

        pasta_pol = os.path.join(pasta_mqar, poluente)

        if not os.path.isdir(pasta_pol):
            print(f"Pasta não encontrada: {pasta_pol}")
            continue

        encontrou = False

        for arquivo in os.listdir(pasta_pol):

            if not arquivo.lower().endswith(".csv"):
                continue

            # Nome sem .csv
            nome = os.path.splitext(arquivo)[0]

            # Exemplo:
            # BA0001ND007
            if len(nome) < 9:
                continue

            id_arquivo = nome[:6]
            cod_arquivo = nome[-3:]

            if id_arquivo == id_mma and cod_arquivo == cod:

                # Salva SEM a extensão .csv
                df.at[i, "ID_MMA_COMPLETO"] = nome

                preenchidos += 1
                encontrou = True
                break

        if not encontrou:
            print(
                f"Não encontrado -> "
                f"POLUENTE={poluente} | "
                f"ID_MMA={id_mma} | "
                f"COD_POLUENTE={cod}"
            )

    df.to_csv(arquivo_csv, index=False)

    print("\n===================================")
    print(f"{preenchidos} registros preenchidos.")
    print(f"Arquivo salvo em:\n{arquivo_csv}")
    print("===================================")