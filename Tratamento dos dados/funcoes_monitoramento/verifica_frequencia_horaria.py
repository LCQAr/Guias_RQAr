import pandas as pd


def verifica_frequencia_horaria(caminho_arquivo):
    """
    Verifica se os registros de DATETIME possuem frequência horária.

    A função:
    
    1. Lê o arquivo CSV.
    2. Converte DATETIME para datetime.
    3. Remove DATETIME inválidos apenas da verificação.
    4. Ordena os registros cronologicamente.
    5. Calcula a diferença entre registros consecutivos.
    6. Mostra as frequências encontradas.
    7. Verifica se todos os intervalos são de 1 hora.
    """

    # ==========================================================
    # 1. LÊ O ARQUIVO
    # ==========================================================

    df = pd.read_csv(
        caminho_arquivo
    )

    # ==========================================================
    # 2. CONVERTE DATETIME
    # ==========================================================

    df["DATETIME"] = pd.to_datetime(
        df["DATETIME"],
        errors="coerce"
    )

    # ==========================================================
    # 3. REMOVE DATETIME INVÁLIDO
    # ==========================================================

    estacao = df.dropna(
        subset=["DATETIME"]
    ).copy()

    # ==========================================================
    # 4. ORDENA PELO HORÁRIO
    # ==========================================================

    estacao = estacao.sort_values(
        "DATETIME"
    )

    # ==========================================================
    # 5. CALCULA DIFERENÇAS
    # ==========================================================

    diferencas = (
        estacao["DATETIME"]
        .diff()
        .dropna()
    )

    # ==========================================================
    # 6. VERIFICA SE EXISTEM INTERVALOS
    # ==========================================================

    if diferencas.empty:

        print(
            "Não existem registros suficientes "
            "para verificar a frequência."
        )

        return

    # ==========================================================
    # 7. CONTA AS FREQUÊNCIAS
    # ==========================================================

    frequencias = (
        diferencas
        .value_counts()
        .sort_index()
    )

    print("Frequência dos registros:")
    print(frequencias)

    # ==========================================================
    # 8. FREQUÊNCIA MAIS COMUM
    # ==========================================================

    frequencia_principal = (
        diferencas
        .value_counts()
        .index[0]
    )

    print(
        f"\nA frequência mais comum dos dados é: "
        f"{frequencia_principal}"
    )

    # ==========================================================
    # 9. VERIFICA SE É HORÁRIA
    # ==========================================================

    uma_hora = pd.Timedelta(hours=1)

    if (diferencas == uma_hora).all():

        print(
            "✓ Todos os registros possuem "
            "frequência horária."
        )

    else:

        print(
            "⚠ Atenção: existem intervalos "
            "diferentes de 1 hora."
        )

        # ------------------------------------------------------
        # Mostra quais intervalos diferentes de 1 hora existem
        # ------------------------------------------------------

        frequencias_nao_horarias = frequencias[
            frequencias.index != uma_hora
        ]

        if not frequencias_nao_horarias.empty:

            print(
                "\nIntervalos diferentes de 1 hora:"
            )

            print(
                frequencias_nao_horarias
            )