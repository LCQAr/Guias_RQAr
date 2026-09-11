import pandas as pd


def corrige_datetime_MQAr(df, nome_arquivo="arquivo"):
    """
    Corrige lacunas de DATETIME em arquivos antigos do MQAr.

    A função procura blocos de linhas consecutivas com DATETIME
    ausente.

    Existem dois casos:

    1. O DATETIME válido anterior e posterior possuem diferença
       de exatamente 1 hora:
           - se a linha intermediária não possui VALOR, ela é removida;
           - se possui VALOR, gera erro, pois não é possível
             determinar um horário válido para essa medição.

    2. Existe uma lacuna horária real:
           exemplo:
           16:30 | VALOR
           NaT   | NaN
           NaT   | NaN
           NaT   | NaN
           21:30 | VALOR

       Nesse caso, os DATETIME intermediários são preenchidos
       de hora em hora. Os valores existentes são mantidos e
       os valores ausentes permanecem como NA.

    A função retorna o DataFrame corrigido.
    """

    df = df.copy()

    # ----------------------------------------------------------
    # 1. Converte DATETIME
    # ----------------------------------------------------------

    df["DATETIME"] = pd.to_datetime(
        df["DATETIME"],
        errors="coerce"
    )

    # ----------------------------------------------------------
    # 2. Identifica linhas com DATETIME ausente
    # ----------------------------------------------------------

    linhas_invalidas = df["DATETIME"].isna()

    if not linhas_invalidas.any():

        return df

    print(
        f"\nCorrigindo DATETIME: {nome_arquivo}"
    )

    quantidade_inicial = linhas_invalidas.sum()

    print(
        f"Linhas com DATETIME ausente encontradas: "
        f"{quantidade_inicial}"
    )

    # ----------------------------------------------------------
    # 3. Identifica blocos consecutivos de DATETIME ausente
    # ----------------------------------------------------------

    grupos = (
        linhas_invalidas
        .ne(linhas_invalidas.shift())
        .cumsum()
    )

    indices_blocos = (
        df[linhas_invalidas]
        .groupby(grupos[linhas_invalidas])
        .groups
    )

    indices_remover = []

    # ----------------------------------------------------------
    # 4. Analisa cada bloco
    # ----------------------------------------------------------

    for indices in indices_blocos.values():

        indices = list(indices)

        primeiro_indice = indices[0]
        ultimo_indice = indices[-1]

        # ------------------------------------------------------
        # 4.1 Procura DATETIME anterior
        # ------------------------------------------------------

        indices_anteriores = df.index[
            df.index < primeiro_indice
        ]

        if len(indices_anteriores) == 0:

            raise ValueError(
                f"Não existe DATETIME anterior à lacuna "
                f"no arquivo {nome_arquivo}. "
                f"Não é possível determinar os horários."
            )

        indice_anterior = indices_anteriores[-1]

        datetime_anterior = (
            df.loc[indice_anterior, "DATETIME"]
        )

        # ------------------------------------------------------
        # 4.2 Procura DATETIME posterior
        # ------------------------------------------------------

        indices_posteriores = df.index[
            df.index > ultimo_indice
        ]

        if len(indices_posteriores) == 0:

            raise ValueError(
                f"Não existe DATETIME posterior à lacuna "
                f"no arquivo {nome_arquivo}. "
                f"Não é possível determinar os horários."
            )

        indice_posterior = indices_posteriores[0]

        datetime_posterior = (
            df.loc[indice_posterior, "DATETIME"]
        )

        # ------------------------------------------------------
        # 4.3 Calcula diferença entre os horários
        # ------------------------------------------------------

        diferenca = (
            datetime_posterior
            - datetime_anterior
        )

        quantidade_linhas = len(indices)

        # ======================================================
        # CASO 1
        # Não existe horário faltando
        # ======================================================

        if diferenca == pd.Timedelta(hours=1):

            valores_preenchidos = []

            for indice in indices:

                valor = df.loc[indice, "VALOR"]

                if pd.notna(valor):

                    if str(valor).strip().lower() not in [
                        "",
                        "nan",
                        "none",
                        "nat"
                    ]:
                        valores_preenchidos.append(indice)

            # --------------------------------------------------
            # Se houver VALOR, não podemos simplesmente apagar
            # a medição.
            # --------------------------------------------------

            if valores_preenchidos:

                raise ValueError(
                    f"Existe uma linha sem DATETIME, mas com "
                    f"VALOR preenchido em {nome_arquivo}. "
                    f"Índices: {valores_preenchidos}. "
                    f"Não é possível determinar o horário."
                )

            # --------------------------------------------------
            # Linha sem DATETIME e sem VALOR: remove
            # --------------------------------------------------

            indices_remover.extend(indices)

            print(
                f"  • Removidas {quantidade_linhas} linha(s) "
                f"vazia(s): "
                f"{datetime_anterior} → {datetime_posterior}"
            )

        # ======================================================
        # CASO 2
        # Existe uma lacuna horária real
        # ======================================================

        else:

            horarios_esperados = pd.date_range(
                start=datetime_anterior
                + pd.Timedelta(hours=1),
                end=datetime_posterior
                - pd.Timedelta(hours=1),
                freq="h"
            )

            # --------------------------------------------------
            # Verifica se a quantidade de horários esperados
            # corresponde à quantidade de linhas vazias.
            # --------------------------------------------------

            if len(horarios_esperados) != quantidade_linhas:

                raise ValueError(
                    f"A lacuna de DATETIME em {nome_arquivo} "
                    f"não possui quantidade de linhas compatível.\n"
                    f"Anterior: {datetime_anterior}\n"
                    f"Posterior: {datetime_posterior}\n"
                    f"Linhas vazias: {quantidade_linhas}\n"
                    f"Horários esperados: "
                    f"{len(horarios_esperados)}"
                )

            # --------------------------------------------------
            # Preenche os DATETIME
            # --------------------------------------------------

            for indice, horario in zip(
                indices,
                horarios_esperados
            ):

                df.loc[indice, "DATETIME"] = horario

            # --------------------------------------------------
            # Conta quantas linhas possuem VALOR
            # --------------------------------------------------

            quantidade_valores = 0

            for indice in indices:

                valor = df.loc[indice, "VALOR"]

                if pd.notna(valor):

                    if str(valor).strip().lower() not in [
                        "",
                        "nan",
                        "none",
                        "nat"
                    ]:
                        quantidade_valores += 1

            print(
                f"  • Preenchida lacuna: "
                f"{datetime_anterior} → "
                f"{datetime_posterior}"
            )

            print(
                f"    {quantidade_linhas} horário(s) "
                f"recuperado(s), "
                f"{quantidade_valores} com VALOR "
                f"e {quantidade_linhas - quantidade_valores} "
                f"sem VALOR."
            )

    # ----------------------------------------------------------
    # 5. Remove linhas identificadas como desnecessárias
    # ----------------------------------------------------------

    if indices_remover:

        df = df.drop(
            index=indices_remover
        )

        df = df.reset_index(
            drop=True
        )

    # ----------------------------------------------------------
    # 6. Verificação final
    # ----------------------------------------------------------

    quantidade_invalidos = (
        df["DATETIME"].isna().sum()
    )

    if quantidade_invalidos > 0:

        raise ValueError(
            f"Ainda existem {quantidade_invalidos} "
            f"DATETIME inválidos após a correção "
            f"de {nome_arquivo}."
        )

    print(
        "  ✓ Correção do DATETIME concluída."
    )

    return df