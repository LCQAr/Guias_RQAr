import pandas as pd


def verifica_horarios_faltantes(caminho_arquivo):
    """
    Verifica e completa lacunas horárias no arquivo.

    A função:

    1. Verifica se a coluna DATETIME existe.
    2. Verifica se existem DATETIME inválidos.
       - Não remove esses registros.
       - Interrompe a execução para que sejam corrigidos
         por uma função específica.
    3. Verifica se existem DATETIME duplicados.
    4. Ordena os registros por DATETIME.
    5. Procura lacunas entre registros consecutivos.
    6. Mostra as lacunas de forma resumida, indicando:
       - primeiro horário da lacuna;
       - último horário antes da retomada dos dados;
       - quantidade de horários faltantes.
    7. Preenche somente essas lacunas com NaN.
    8. Salva o arquivo atualizado.
    """

    # ==========================================================
    # 1. LÊ O ARQUIVO
    # ==========================================================

    df = pd.read_csv(
        caminho_arquivo
    )

    # ==========================================================
    # 2. VERIFICA A COLUNA DATETIME
    # ==========================================================

    if "DATETIME" not in df.columns:

        raise ValueError(
            "A coluna 'DATETIME' não existe no arquivo."
        )

    # ==========================================================
    # 3. CONVERTE DATETIME
    # ==========================================================

    datetime_convertido = pd.to_datetime(
        df["DATETIME"],
        errors="coerce"
    )

    # ==========================================================
    # 4. VERIFICA DATETIME INVÁLIDO
    # ==========================================================

    quantidade_invalidos = (
        datetime_convertido.isna().sum()
    )

    if quantidade_invalidos > 0:

        print(
            f"ATENÇÃO: foram encontrados "
            f"{quantidade_invalidos} registros com "
            f"DATETIME inválido."
        )

        print(
            "→ Os registros NÃO serão removidos."
        )

        print(
            "→ Corrija os DATETIME inválidos antes "
            "de completar os horários."
        )

        raise ValueError(
            "Existem DATETIME inválidos no arquivo."
        )

    print(
        "Todos os registros possuem DATETIME válido."
    )

    df["DATETIME"] = datetime_convertido

    # ==========================================================
    # 5. VERIFICA DUPLICIDADES
    # ==========================================================

    duplicados = df[
        df["DATETIME"].duplicated(
            keep=False
        )
    ]

    if not duplicados.empty:

        horarios_duplicados = (
            duplicados["DATETIME"]
            .dt.strftime("%Y-%m-%d %H:%M:%S")
            .unique()
            .tolist()
        )

        raise ValueError(
            "Foram encontrados DATETIME duplicados: "
            f"{horarios_duplicados}"
        )

    # ==========================================================
    # 6. ORDENA OS DADOS
    # ==========================================================

    df = df.sort_values(
        "DATETIME"
    ).reset_index(drop=True)

    # ==========================================================
    # 7. CALCULA DIFERENÇA ENTRE REGISTROS
    # ==========================================================

    diferencas = (
        df["DATETIME"]
        .diff()
    )

    # ==========================================================
    # 8. IDENTIFICA ONDE EXISTEM LACUNAS
    # ==========================================================

    indices_lacunas = []

    for i in range(1, len(df)):

        diferenca = diferencas.iloc[i]

        if diferenca > pd.Timedelta(hours=1):

            indices_lacunas.append(i)

    # ==========================================================
    # 9. VERIFICA SE EXISTEM LACUNAS
    # ==========================================================

    if len(indices_lacunas) == 0:

        print(
            "Não foram encontradas lacunas horárias."
        )

        return

    print(
        f"ATENÇÃO: foram encontradas "
        f"{len(indices_lacunas)} lacunas horárias."
    )

    print("\nLacunas encontradas:")

    # Guarda os horários que serão adicionados
    todos_horarios_faltantes = []

    # ==========================================================
    # 10. MOSTRA AS LACUNAS
    # ==========================================================

    for indice in indices_lacunas:

        horario_anterior = (
            df.loc[indice - 1, "DATETIME"]
        )

        horario_posterior = (
            df.loc[indice, "DATETIME"]
        )

        # Primeiro horário que está faltando
        inicio_lacuna = (
            horario_anterior
            + pd.Timedelta(hours=1)
        )

        # Último horário que está faltando
        fim_lacuna = (
            horario_posterior
            - pd.Timedelta(hours=1)
        )

        # Cria os horários faltantes
        horarios_faltantes = pd.date_range(
            start=inicio_lacuna,
            end=fim_lacuna,
            freq="h"
        )

        todos_horarios_faltantes.extend(
            horarios_faltantes
        )

        print(
            f"  • Lacuna: "
            f"{horario_anterior.strftime('%Y-%m-%d %H:%M:%S')} "
            f"→ "
            f"{horario_posterior.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        print(
            f"    {len(horarios_faltantes)} "
            f"horário(s) faltante(s)."
        )

    # ==========================================================
    # 11. CRIA AS LINHAS FALTANTES
    # ==========================================================

    novas_linhas = pd.DataFrame(
        {
            "DATETIME": todos_horarios_faltantes
        }
    )

    # Cria as demais colunas como NaN
    for coluna in df.columns:

        if coluna != "DATETIME":

            novas_linhas[coluna] = pd.NA

    # Garante a mesma ordem das colunas
    novas_linhas = novas_linhas[
        df.columns
    ]

    # ==========================================================
    # 12. JUNTA OS DADOS
    # ==========================================================

    df = pd.concat(
        [
            df,
            novas_linhas
        ],
        ignore_index=True
    )

    # ==========================================================
    # 13. ORDENA NOVAMENTE
    # ==========================================================

    df = df.sort_values(
        "DATETIME"
    ).reset_index(drop=True)

    # ==========================================================
    # 14. SALVA
    # ==========================================================

    df.to_csv(
        caminho_arquivo,
        index=False,
        encoding="utf-8",
        sep=","
    )

    print(
        f"\n✓ {len(todos_horarios_faltantes)} "
        "horários faltantes foram preenchidos com NaN."
    )

    print(
        "✓ Arquivo atualizado com sucesso!"
    )