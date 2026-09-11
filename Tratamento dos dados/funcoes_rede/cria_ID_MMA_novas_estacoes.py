import pandas as pd
import os

def preencher_id_mma(
    uf,
    ano,
    pasta_base="/home/nobre/Notebooks/RQAr/dados/dados_formatados"
):
    """
    Cria ID_MMA apenas para novas estações.

    Regras:
    - Nunca altera um ID_MMA existente.
    - Cada ID_OEMA recebe um único ID_MMA.
    - A sequência continua a partir do maior ID_MMA existente na UF.
    - Se houver INICIO válido, as novas estações são ordenadas pela
      data mais antiga.
    - Estações sem INICIO ficam depois das estações com data.
    - Entre estações sem INICIO, a ordem é alfabética pelo ID_OEMA.
    - Se nenhuma estação tiver INICIO, todas são ordenadas por ID_OEMA.
    """

    uf = str(uf).strip().upper()

    caminho_csv = os.path.join(
        pasta_base, str(ano), "rede", f"{uf}_Rede_{ano}.csv"
    )

    if not os.path.exists(caminho_csv):
        raise FileNotFoundError(
            f"Arquivo não encontrado:\n{caminho_csv}"
        )

    df = pd.read_csv(caminho_csv, encoding="utf-8-sig")

    colunas_necessarias = ["INICIO", "ID_OEMA", "ID_MMA", "UF"]
    colunas_faltantes = [
        coluna for coluna in colunas_necessarias
        if coluna not in df.columns
    ]

    if colunas_faltantes:
        raise ValueError(
            "As seguintes colunas não foram encontradas: "
            + ", ".join(colunas_faltantes)
        )

    # INICIO já foi padronizado anteriormente
    df["INICIO"] = pd.to_datetime(
        df["INICIO"],
        errors="coerce"
    )

    df["UF"] = (
        df["UF"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Completa registros vazios de estações que já possuem ID_MMA
    for id_oema, grupo in df.groupby("ID_OEMA"):
        ids_existentes = (
            grupo["ID_MMA"]
            .dropna()
            .astype(str)
            .str.strip()
        )

        ids_existentes = ids_existentes[
            ids_existentes != ""
        ]

        if len(ids_existentes) > 0:
            id_mma = ids_existentes.iloc[0]

            mascara = (
                (df["ID_OEMA"] == id_oema)
                &
                (
                    df["ID_MMA"].isna()
                    |
                    (
                        df["ID_MMA"]
                        .astype(str)
                        .str.strip()
                        == ""
                    )
                )
            )

            df.loc[mascara, "ID_MMA"] = id_mma

    # Seleciona somente a UF informada
    df_uf = df[df["UF"] == uf].copy()

    # Descobre o maior número de ID_MMA já existente
    ultimo = 0

    for codigo in (
        df_uf["ID_MMA"]
        .dropna()
        .astype(str)
        .str.strip()
    ):
        if codigo == "":
            continue

        if "_" in codigo:
            numero = codigo.split("_")[-1]
        else:
            numero = codigo.replace(uf, "", 1)

        try:
            ultimo = max(ultimo, int(numero))
        except (ValueError, TypeError):
            continue

    # Agrupa os registros por estação
    estacoes = (
        df_uf
        .groupby("ID_OEMA")
        .agg(
            INICIO=("INICIO", "min"),
            ID_MMA=(
                "ID_MMA",
                lambda x:
                    x.dropna().iloc[0]
                    if len(x.dropna()) > 0
                    else ""
            )
        )
        .reset_index()
    )

    # Mantém apenas estações que ainda não possuem ID_MMA
    estacoes = estacoes[
        estacoes["ID_MMA"]
        .astype(str)
        .str.strip()
        == ""
    ].copy()

    # Define a ordem de criação dos novos ID_MMA
    if len(estacoes) > 0:
        tem_data = estacoes["INICIO"].notna().any()

        if tem_data:
            # Datas primeiro; sem data por último.
            # ID_OEMA é usado como critério de desempate.
            estacoes = estacoes.sort_values(
                by=["INICIO", "ID_OEMA"],
                na_position="last"
            )
        else:
            # Se nenhuma estação tiver data,
            # usa somente a ordem alfabética do ID_OEMA.
            estacoes = estacoes.sort_values(
                by="ID_OEMA"
            )

    # Cria os novos ID_MMA
    novos_ids = 0

    for _, linha in estacoes.iterrows():
        ultimo += 1
        novos_ids += 1

        novo_id = f"{uf}{ultimo:04d}"

        mascara = df["ID_OEMA"] == linha["ID_OEMA"]
        df.loc[mascara, "ID_MMA"] = novo_id

    # Salva as alterações no mesmo arquivo
    df.to_csv(
        caminho_csv,
        index=False,
        encoding="utf-8-sig"
    )

    print("ID_MMA preenchidos com sucesso!")
    print(f"Novas estações: {novos_ids}")
    print(f"Último ID_MMA utilizado: {uf}{ultimo:04d}")
    print(f"Arquivo atualizado: {caminho_csv}")