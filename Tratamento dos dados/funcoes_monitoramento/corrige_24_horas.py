import pandas as pd
from datetime import timedelta


def corrige_24_horas(caminho_arquivo):
    """
    Verifica se existe algum DATETIME contendo 24:00.

    Quando encontra:
    - transforma 24:00 em 00:00;
    - soma um dia à data;
    - mantém as demais colunas do arquivo sem alterações.

    A função não define um formato fixo para as demais datas.
    A padronização definitiva do DATETIME será feita posteriormente
    pela função padroniza_datetime().
    """

    # ==========================================================
    # 1. LÊ O ARQUIVO
    # ==========================================================

    df = pd.read_csv(
        caminho_arquivo,
        dtype=str
    )

    # ==========================================================
    # 2. VERIFICA SE DATETIME EXISTE
    # ==========================================================

    if "DATETIME" not in df.columns:

        raise ValueError(
            "A coluna 'DATETIME' não existe no arquivo."
        )

    # ==========================================================
    # 3. GUARDA DATETIME COMO TEXTO
    # ==========================================================

    df["DATETIME"] = (
        df["DATETIME"]
        .astype(str)
        .str.strip()
    )

    # ==========================================================
    # 4. VERIFICA SE EXISTEM HORÁRIOS 24:00
    # ==========================================================

    possui_24 = (
        df["DATETIME"]
        .str.endswith("24:00")
        .any()
    )

    if possui_24:

        print("Foram encontradas medições com horário 24:00.")

    else:

        print("Não foram encontradas medições com horário 24:00.")

    # ==========================================================
    # 5. CORRIGE OS REGISTROS
    # ==========================================================

    def ajusta_data_hora(valor):

        if pd.isna(valor):

            return pd.NaT

        valor = str(valor).strip()

        if valor == "" or valor.lower() == "nan":

            return pd.NaT

        # ------------------------------------------------------
        # Caso seja 24:00
        # ------------------------------------------------------

        if valor.endswith("24:00"):

            # Substitui somente o 24:00 por 00:00
            novo_valor = (
                valor[:-5] + "00:00"
            )

            # Tenta interpretar a data sem impor
            # um formato específico
            dt = pd.to_datetime(
                novo_valor,
                errors="coerce"
            )

            if pd.notna(dt):

                dt += timedelta(days=1)

            return dt

        # ------------------------------------------------------
        # Demais horários
        # ------------------------------------------------------

        return pd.to_datetime(
            valor,
            errors="coerce"
        )

    # Aplica somente na coluna DATETIME
    df["DATETIME"] = (
        df["DATETIME"]
        .apply(ajusta_data_hora)
    )

    # ==========================================================
    # 6. VERIFICA SE ALGUM DATETIME FICOU INVÁLIDO
    # ==========================================================

    quantidade_invalidos = (
        df["DATETIME"].isna().sum())

    if quantidade_invalidos > 0:

        raise ValueError(
            f"Após a correção, {quantidade_invalidos} "
            "registro(s) possuem DATETIME inválido."
        )

    # ==========================================================
    # 7. SALVA O ARQUIVO
    # ==========================================================

    df.to_csv(
        caminho_arquivo,
        index=False,
        encoding="utf-8",
        sep=","
    )

    print("Correção do horário concluída!")