import pandas as pd


def preencher_cod_uf_ibge(uf: str):
    """
    Preenche a coluna COD_UF_IBGE utilizando a coluna UF.

    O arquivo da rede de monitoramento é localizado automaticamente
    a partir da UF informada.

    A função realiza as seguintes etapas:
    - Monta automaticamente o caminho do arquivo CSV da rede a partir da UF.
    - Lê o arquivo da rede de monitoramento.
    - Lê o dicionário oficial de códigos das UFs do IBGE.
    - Normaliza as siglas das UFs.
    - Busca o código IBGE correspondente a cada UF.
    - Preenche a coluna COD_UF_IBGE.
    - Salva o arquivo atualizado no mesmo caminho.

    Parâmetros
    ----------
    uf : str
        Sigla da Unidade Federativa (UF) correspondente ao arquivo
        da rede de monitoramento.

    Retorna
    -------
    None
        O arquivo CSV é atualizado diretamente no caminho
        correspondente à UF informada.

    Exemplo
    -------
    preencher_cod_uf_ibge("SC")

    O arquivo utilizado será:
        /home/nobre/Notebooks/RQAr/dados/dados_formatados/2025/rede/SC_Rede_2025.csv
    """

    # Caminho da pasta da rede
    pasta_rede = (
        "/home/nobre/Notebooks/RQAr/"
        "dados/dados_formatados/2025/rede"
    )

    # Monta automaticamente o caminho conforme a UF
    caminho_arquivo = (
        f"{pasta_rede}/{uf.upper()}_Rede_2025.csv"
    )

    # Caminho fixo do dicionário IBGE
    caminho_dicionario = (
        "/home/nobre/Notebooks/RQAr/"
        "dicionarios/IBGE_UFS_CODIGOS.csv"
    )

    # Lê os arquivos
    df = pd.read_csv(
        caminho_arquivo,
        dtype=str
    )

    df_ibge = pd.read_csv(
        caminho_dicionario,
        dtype=str
    )

    # Remove espaços e padroniza para maiúsculas
    df["UF"] = (
        df["UF"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df_ibge["UF"] = (
        df_ibge["UF"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Cria o dicionário UF -> CODIGO
    mapa_codigos = dict(
        zip(
            df_ibge["UF"],
            df_ibge["CODIGOS"]
        )
    )

    # Preenche COD_UF_IBGE
    df["COD_UF_IBGE"] = (
        df["UF"].map(mapa_codigos)
    )

    # Salva o arquivo
    df.to_csv(
        caminho_arquivo,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        "✅ Coluna COD_UF_IBGE preenchida com sucesso!"
    )

    print(
        f"Arquivo atualizado:\n{caminho_arquivo}"
    )