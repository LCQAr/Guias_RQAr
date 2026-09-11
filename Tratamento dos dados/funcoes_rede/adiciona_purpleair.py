import os
import re
import unicodedata
import pandas as pd

def adicionar_purpleair(
    uf,
    caminho_base="/home/nobre/Notebooks/RQAr/dados/Monitoramento_QAr_BR_2025.csv",
    pasta_rede="/home/nobre/Notebooks/RQAr/dados/dados_formatados/2025/rede",
):
    """
    Adiciona à planilha da rede as linhas da base nacional
    cuja FONTE seja 'PurpleAir 2025'.

    Regras:
    - Filtra pela UF informada.
    - Seleciona somente FONTE = 'PurpleAir 2025'.
    - O ID_OEMA da base nacional é colocado em ID_OEMA_ORIGINAL.
    - O ID_OEMA da base NÃO é copiado diretamente para ID_OEMA.
    - ID_OEMA é preenchido somente quando estiver vazio,
      usando ID_OEMA_ORIGINAL padronizado.
    - ID_OEMA já existente na rede é preservado.
    - Todos os ID_OEMA ficam padronizados.
    - "Nao declarado" é transformado em vazio.
    - Não duplica linhas que já estejam na rede.
    """

    # ==========================================================
    # 1. FUNÇÃO PARA PADRONIZAR ID_OEMA
    # ==========================================================

    def padronizar_id_oema(texto):

        # Se estiver vazio, mantém vazio
        if pd.isna(texto):
            return texto

        # Converte para texto e coloca em minúsculo
        texto = str(texto).lower()

        # ------------------------------------------------------
        # Remove acentos
        # ------------------------------------------------------

        texto = unicodedata.normalize(
            "NFKD",
            texto
        )

        texto = "".join(
            caractere
            for caractere in texto
            if not unicodedata.combining(caractere)
        )

        # ------------------------------------------------------
        # Substitui espaços e hífens por "_"
        # ------------------------------------------------------

        texto = re.sub(
            r"[\s-]+",
            "_",
            texto
        )

        # ------------------------------------------------------
        # Remove caracteres especiais
        # Mantém somente letras, números e "_"
        # ------------------------------------------------------

        texto = re.sub(
            r"[^a-z0-9_]",
            "",
            texto
        )

        # ------------------------------------------------------
        # Remove "_" repetidos
        # ------------------------------------------------------

        texto = re.sub(
            r"_+",
            "_",
            texto
        )

        # ------------------------------------------------------
        # Remove "_" do início e final
        # ------------------------------------------------------

        texto = texto.strip("_")

        return texto

    # ==========================================================
    # 2. CAMINHO DO ARQUIVO DA REDE
    # ==========================================================

    caminho_rede = os.path.join(
        pasta_rede,
        f"{uf}_Rede_2025.csv"
    )

    # ==========================================================
    # 3. LER ARQUIVOS
    # ==========================================================

    df_base = pd.read_csv(
        caminho_base,
        encoding="utf-8"
    )

    df_rede = pd.read_csv(
        caminho_rede,
        encoding="utf-8"
    )

    # ==========================================================
    # 4. PADRONIZAR NOMES DAS COLUNAS
    # ==========================================================

    df_base.columns = (
        df_base.columns
        .astype(str)
        .str.strip()
    )

    df_rede.columns = (
        df_rede.columns
        .astype(str)
        .str.strip()
    )

    # ==========================================================
    # 5. TRANSFORMAR "Nao declarado" EM VAZIO
    # ==========================================================

    df_base = df_base.replace(
        "Nao declarado",
        pd.NA
    )

    df_rede = df_rede.replace(
        "Nao declarado",
        pd.NA
    )

    # ==========================================================
    # 6. FILTRAR PURPLEAIR
    # ==========================================================

    df_purpleair = df_base[
        (
            df_base["UF"]
            .astype(str)
            .str.strip()
            == str(uf).strip()
        )
        &
        (
            df_base["FONTE"]
            .astype(str)
            .str.strip()
            .str.lower()
            == "purpleair 2025"
        )
    ].copy()

    if df_purpleair.empty:

        print(
            f"Nenhuma linha PurpleAir 2025 "
            f"encontrada para {uf}."
        )

        return

    # ==========================================================
    # 7. TRATAMENTO DO ID_OEMA DA BASE
    # ==========================================================
    #
    # ID_OEMA da base nacional:
    #
    #       ID_OEMA
    #          ↓
    #   ID_OEMA_ORIGINAL
    #
    # E NÃO será mantido em ID_OEMA.
    # ==========================================================

    if "ID_OEMA" in df_purpleair.columns:

        # Cria/atualiza ID_OEMA_ORIGINAL
        if "ID_OEMA_ORIGINAL" not in df_purpleair.columns:
            df_purpleair["ID_OEMA_ORIGINAL"] = (
                df_purpleair["ID_OEMA"]
            )
        else:
            df_purpleair["ID_OEMA_ORIGINAL"] = (
                df_purpleair["ID_OEMA"]
            )

        # NÃO trazer o ID_OEMA da base diretamente
        df_purpleair["ID_OEMA"] = pd.NA

    else:

        if "ID_OEMA_ORIGINAL" not in df_purpleair.columns:
            df_purpleair["ID_OEMA_ORIGINAL"] = pd.NA

        if "ID_OEMA" not in df_purpleair.columns:
            df_purpleair["ID_OEMA"] = pd.NA

    # ==========================================================
    # 8. GARANTIR ID_OEMA_ORIGINAL NA REDE
    # ==========================================================

    if "ID_OEMA_ORIGINAL" not in df_rede.columns:

        df_rede["ID_OEMA_ORIGINAL"] = pd.NA

    # ==========================================================
    # 9. GARANTIR QUE A REDE TENHA TODAS AS COLUNAS DA BASE
    # ==========================================================

    for coluna in df_purpleair.columns:

        if coluna not in df_rede.columns:

            df_rede[coluna] = pd.NA

    # ==========================================================
    # 10. PREPARAR LINHAS PARA ADICIONAR
    # ==========================================================

    df_adicionar = df_purpleair.copy()

    # Garante todas as colunas da rede
    for coluna in df_rede.columns:

        if coluna not in df_adicionar.columns:

            df_adicionar[coluna] = pd.NA

    # Mantém exatamente a ordem das colunas da rede
    df_adicionar = df_adicionar[
        df_rede.columns
    ]

    # ==========================================================
    # 11. IDENTIFICAR LINHAS QUE JÁ EXISTEM
    # ==========================================================

    colunas_comuns = [
        coluna
        for coluna in df_purpleair.columns
        if coluna in df_rede.columns
    ]

    # Não utilizar IDs na comparação
    colunas_excluir = {
        "FONTE",
        "ID_OEMA",
        "ID_OEMA_ORIGINAL"
    }

    colunas_comparacao = [
        coluna
        for coluna in colunas_comuns
        if coluna not in colunas_excluir
    ]

    # ==========================================================
    # 12. VERIFICAR DUPLICIDADES
    # ==========================================================

    if colunas_comparacao:

        # ------------------------------------------------------
        # Chave das linhas existentes na rede
        # ------------------------------------------------------

        chave_rede = (
            df_rede[colunas_comparacao]
            .fillna("")
            .astype(str)
            .apply(
                lambda linha: "||".join(
                    linha.str.strip()
                ),
                axis=1
            )
        )

        # ------------------------------------------------------
        # Chave das linhas PurpleAir
        # ------------------------------------------------------

        chave_purpleair = (
            df_adicionar[colunas_comparacao]
            .fillna("")
            .astype(str)
            .apply(
                lambda linha: "||".join(
                    linha.str.strip()
                ),
                axis=1
            )
        )

        # ------------------------------------------------------
        # Somente linhas novas
        # ------------------------------------------------------

        mascara_nova = (
            ~chave_purpleair.isin(
                set(chave_rede)
            )
        )

        df_adicionar = (
            df_adicionar[
                mascara_nova
            ]
            .copy()
        )

    # ==========================================================
    # 13. QUANTIDADE DE LINHAS NOVAS
    # ==========================================================

    quantidade_adicionada = len(
        df_adicionar
    )

    # ==========================================================
    # 14. ADICIONAR PURPLEAIR
    # ==========================================================

    if quantidade_adicionada > 0:

        df_rede = pd.concat(
            [
                df_rede,
                df_adicionar
            ],
            ignore_index=True
        )

        # ======================================================
        # 15. TRANSFORMAR "Nao declarado" EM VAZIO
        # ======================================================

        df_rede = df_rede.replace(
            "Nao declarado",
            pd.NA
        )

        # ======================================================
        # 16. PADRONIZAR ID_OEMA_ORIGINAL
        #     PARA USAR NO PREENCHIMENTO
        # ======================================================

        id_oema_original_padronizado = (
            df_rede["ID_OEMA_ORIGINAL"]
            .apply(padronizar_id_oema)
        )

        # ======================================================
        # 17. PREENCHER ID_OEMA SOMENTE SE ESTIVER VAZIO
        # ======================================================

        df_rede["ID_OEMA"] = (
            df_rede["ID_OEMA"]
            .fillna(
                id_oema_original_padronizado
            )
        )

        # ======================================================
        # 18. GARANTIR QUE TODO ID_OEMA FIQUE PADRONIZADO
        # ======================================================

        df_rede["ID_OEMA"] = (
            df_rede["ID_OEMA"]
            .apply(padronizar_id_oema)
        )

        # ======================================================
        # 19. SALVAR ARQUIVO
        # ======================================================

        df_rede.to_csv(
            caminho_rede,
            index=False,
            encoding="utf-8"
        )

        print(
            f"{quantidade_adicionada} linhas PurpleAir 2025 "
            f"adicionadas à rede de {uf}."
        )

    else:

        print(
            f"Nenhuma nova linha PurpleAir 2025 "
            f"precisa ser adicionada à rede de {uf}."
        )

    print(
        f"Arquivo atualizado: {caminho_rede}"
    )