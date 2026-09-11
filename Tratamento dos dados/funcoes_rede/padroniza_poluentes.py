import pandas as pd
def padronizar_poluentes(uf: str, ano: int):
    """
    Padroniza as colunas de poluentes utilizando o dicionário oficial.

    O arquivo da rede de monitoramento é localizado automaticamente
    a partir da UF e do ano informados.

    A função realiza as seguintes etapas:
    - Monta automaticamente o caminho do arquivo CSV da rede a partir da UF e do ano.
    - Lê o arquivo CSV contendo os dados da rede de monitoramento.
    - Lê o dicionário oficial de poluentes.
    - Atualiza os nomes dos poluentes para o padrão utilizado pelo projeto.
    - Preenche a coluna COD_POLUENTE de acordo com o dicionário de poluentes.
    - Garante que os códigos dos poluentes possuam três dígitos.
    - Salva o arquivo atualizado no mesmo caminho.

    Parâmetros
    ----------
    uf : str
        Sigla da Unidade Federativa (UF) correspondente ao arquivo
        da rede de monitoramento.

    ano : int
        Ano correspondente ao arquivo da rede de monitoramento.

    Retorna
    -------
    None
        O arquivo CSV é atualizado diretamente no caminho
        correspondente à UF e ao ano informados.

    Exemplo
    -------
    padronizar_poluentes("RJ", 2024)

    O arquivo utilizado será:
        /home/nobre/Notebooks/RQAr/dados/dados_formatados/2024/rede/RJ_Rede_2024.csv
    """

    # ==========================================================
    # CAMINHOS
    # ==========================================================

    pasta_rede = (
        "/home/nobre/Notebooks/RQAr/"
        f"dados/dados_formatados/{ano}/rede"
    )

    caminho_arquivo = (
        f"{pasta_rede}/{uf.upper()}_Rede_{ano}.csv"
    )

    caminho_dicionario = (
        "/home/nobre/Notebooks/RQAr/"
        "dicionarios/CODIGO_POLUENTES.csv"
    )

    # ==========================================================
    # LEITURA DOS ARQUIVOS
    # ==========================================================

    df = pd.read_csv(
        caminho_arquivo,
        dtype=str
    )

    dic = pd.read_csv(
        caminho_dicionario,
        dtype=str
    )

    # Garante que as colunas sejam string
    dic = dic.astype(str)
    df["POLUENTE"] = df["POLUENTE"].astype(str)

    # ==========================================================
    # DICIONÁRIOS DE CONSULTA
    # ==========================================================

    mapa_nome = dict(
        zip(
            dic["POLUENTE"],
            dic["NOME_PASTA"]
        )
    )

    # ==========================================================
    # ATUALIZA POLUENTE
    # ==========================================================

    df["POLUENTE"] = df["POLUENTE"].replace(
        mapa_nome
    )

    # ==========================================================
    # ATUALIZA COD_POLUENTE
    # ==========================================================

    mapa_codigo = dict(
        zip(
            dic["NOME_PASTA"],
            dic["COD_POLUENTE"]
        )
    )

    if "COD_POLUENTE" not in df.columns:
        df["COD_POLUENTE"] = ""

    df["COD_POLUENTE"] = (
        df["POLUENTE"]
        .map(mapa_codigo)
        .fillna(df["COD_POLUENTE"])
        .astype(str)
        .str.zfill(3)
    )

    # ==========================================================
    # SALVA O ARQUIVO
    # ==========================================================

    df.to_csv(
        caminho_arquivo,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"✅ Poluentes padronizados com sucesso: "
        f"{uf.upper()} - {ano}"
    )

    print(
        f"Arquivo atualizado:\n{caminho_arquivo}"
    )