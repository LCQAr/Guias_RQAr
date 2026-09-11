import pandas as pd
import unicodedata
def preencher_cd_mun(
    uf: str,
    coluna_uf: str = "UF",
    coluna_cidade: str = "CIDADE",
    coluna_cd_mun: str = "CD_MUN",
):
    """
    Preenche a coluna de código do município (CD_MUN) utilizando o
    dicionário oficial de municípios do IBGE.

    O arquivo da rede de monitoramento é localizado automaticamente
    a partir da UF informada.

    A função realiza as seguintes etapas:
    - Monta automaticamente o caminho do arquivo CSV da rede a partir da UF.
    - Lê o arquivo CSV contendo os dados da rede de monitoramento.
    - Lê o dicionário oficial de municípios do IBGE.
    - Normaliza os nomes dos municípios para evitar diferenças de
      acentuação, letras maiúsculas/minúsculas e espaços.
    - Busca o código IBGE utilizando a UF e o nome do município.
    - Atualiza a coluna CD_MUN.
    - Salva o arquivo atualizado.

    Parâmetros
    ----------
    uf : str
        Sigla da Unidade Federativa (UF) correspondente ao arquivo
        da rede de monitoramento.

    coluna_uf : str, opcional
        Nome da coluna que contém a sigla da UF.
        Padrão: "UF".

    coluna_cidade : str, opcional
        Nome da coluna que contém o nome do município.
        Padrão: "CIDADE".

    coluna_cd_mun : str, opcional
        Nome da coluna onde será preenchido o código IBGE do município.
        Padrão: "CD_MUN".

    Retorna
    -------
    None
        O arquivo CSV é atualizado diretamente no caminho
        correspondente à UF informada.

    Exemplo
    -------
    preencher_cd_mun("RJ")

    O arquivo utilizado será:
        /home/nobre/Notebooks/RQAr/dados/dados_formatados/2025/rede/RJ_Rede_2025.csv
    """

    # ==========================================================
    # CAMINHOS
    # ==========================================================

    pasta_rede = (
        "/home/nobre/Notebooks/RQAr/"
        "dados/dados_formatados/2025/rede"
    )

    caminho_arquivo = (
        f"{pasta_rede}/{uf.upper()}_Rede_2025.csv"
    )

    caminho_dicionario = (
        "/home/nobre/Notebooks/RQAr/"
        "dicionarios/IBGE_CODIGO_MUN.csv"
    )

    # ==========================================================
    # NORMALIZAÇÃO DOS NOMES
    # ==========================================================

    def normalizar_nome_municipio(nome):
        """Normaliza o nome do município para facilitar a comparação."""

        nome = str(nome).strip().upper()

        nome = unicodedata.normalize(
            "NFKD", nome
        ).encode(
            "ASCII", "ignore"
        ).decode(
            "ASCII"
        )

        nome = " ".join(nome.split())

        return nome

    # ==========================================================
    # LEITURA DOS ARQUIVOS
    # ==========================================================

    df = pd.read_csv(
        caminho_arquivo,
        dtype=str
    )

    dicionario = pd.read_csv(
        caminho_dicionario,
        dtype=str
    )

    # ==========================================================
    # NORMALIZA AS COLUNAS DO DICIONÁRIO
    # ==========================================================

    dicionario["_NOME_TOM_NORM"] = (
        dicionario["MUNICÍPIO - TOM"]
        .apply(normalizar_nome_municipio)
    )

    dicionario["_NOME_IBGE_NORM"] = (
        dicionario["MUNICÍPIO - IBGE"]
        .apply(normalizar_nome_municipio)
    )

    dicionario["_UF_NORM"] = (
        dicionario["UF"]
        .str.strip()
        .str.upper()
    )

    # ==========================================================
    # CRIA MAPAS DE BUSCA
    # ==========================================================

    mapa_tom = dict(
        zip(
            zip(
                dicionario["_UF_NORM"],
                dicionario["_NOME_TOM_NORM"]
            ),
            dicionario["CÓDIGO DO MUNICÍPIO - IBGE"]
        )
    )

    mapa_ibge = dict(
        zip(
            zip(
                dicionario["_UF_NORM"],
                dicionario["_NOME_IBGE_NORM"]
            ),
            dicionario["CÓDIGO DO MUNICÍPIO - IBGE"]
        )
    )

    # ==========================================================
    # PROCURA O CÓDIGO DE CADA MUNICÍPIO
    # ==========================================================

    nao_encontrados = []

    for idx, linha in df.iterrows():

        uf_linha = str(
            linha[coluna_uf]
        ).strip().upper()

        nome_norm = normalizar_nome_municipio(
            linha[coluna_cidade]
        )

        chave = (
            uf_linha,
            nome_norm
        )

        codigo = (
            mapa_tom.get(chave)
            or mapa_ibge.get(chave)
        )

        if codigo is not None:

            df.at[
                idx,
                coluna_cd_mun
            ] = codigo

        else:

            nao_encontrados.append({
                coluna_uf: linha[coluna_uf],
                coluna_cidade: linha[coluna_cidade],
            })

    # ==========================================================
    # RELATÓRIO
    # ==========================================================

    if nao_encontrados:

        print(
            f"⚠️ {len(nao_encontrados)} cidade(s) "
            "não encontradas no dicionário:"
        )

        for item in nao_encontrados:

            print(
                f"   - {item[coluna_uf]} / "
                f"{item[coluna_cidade]}"
            )

    else:

        print(
            "✅ Todas as cidades foram encontradas "
            "no dicionário."
        )

    # ==========================================================
    # SALVA O ARQUIVO ATUALIZADO
    # ==========================================================

    df.to_csv(
        caminho_arquivo,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"Arquivo atualizado:\n{caminho_arquivo}"
    )