import pandas as pd
import unicodedata


def preencher_ID_MMA_COMPLETO(
    UF,
    pasta_rede="/home/nobre/Notebooks/RQAr/dados/dados_formatados/2025/rede",
):
    """
    Preenche a coluna ID_MMA_COMPLETO no formato:

        ID_MMA + CATEGORIA/FUNCIONAMENTO + COD_POLUENTE

    Exemplo:
        MG0006RA001

    Regras:
    --------
    Categoria:
        Referência / Referência ou equivalente / Equivalente -> R
        Indicativa -> I

    Funcionamento:
        Manual -> M
        Automático / Automática -> A

    Caso Categoria OU Funcionamento não sejam reconhecidos,
    utiliza ND.

    COD_POLUENTE sempre com 3 dígitos.

    Não altera nenhuma outra coluna e não sobrescreve
    ID_MMA_COMPLETO já preenchido.
    """

    def normalizar(texto):
        if pd.isna(texto):
            return ""

        texto = str(texto).strip().lower()
        texto = unicodedata.normalize("NFKD", texto)
        texto = texto.encode("ASCII", "ignore").decode("ASCII")

        return texto

    caminho_csv = f"{pasta_rede}/{UF}_Rede_2025.csv"

    df = pd.read_csv(caminho_csv)

    if "ID_MMA_COMPLETO" not in df.columns:
        df["ID_MMA_COMPLETO"] = ""

    for i, row in df.iterrows():

        # Mantém valor existente
        valor_atual = str(row["ID_MMA_COMPLETO"]).strip()

        if (
            not pd.isna(row["ID_MMA_COMPLETO"])
            and valor_atual != ""
            and valor_atual.lower() != "nan"
        ):
            continue

        # ---------------- ID_MMA ----------------

        if pd.isna(row["ID_MMA"]):
            continue

        id_mma = str(row["ID_MMA"]).strip()

        if id_mma == "" or id_mma.lower() == "nan":
            continue

        # ---------------- Categoria ----------------

        categoria = normalizar(row["CATEGORIA"])

        if any(
            palavra in categoria
            for palavra in [
                "referencia",
                "equivalente",
            ]
        ):
            cat = "R"

        elif "indicativa" in categoria:
            cat = "I"

        else:
            cat = None

        # ---------------- Funcionamento ----------------

        funcionamento = normalizar(row["FUNCIONAMENTO"])

        if "manual" in funcionamento:
            func = "M"

        elif any(
            palavra in funcionamento
            for palavra in [
                "automatic",
                "automatica",
                "automatico",
            ]
        ):
            func = "A"

        else:
            func = None

        # ---------------- Letras ----------------

        if cat is None or func is None:
            letras = "ND"
        else:
            letras = cat + func

        # ---------------- COD_POLUENTE ----------------

        try:
            cod = f"{int(float(row['COD_POLUENTE'])):03d}"
        except:
            continue

        # ---------------- Resultado ----------------

        df.at[i, "ID_MMA_COMPLETO"] = f"{id_mma}{letras}{cod}"

    df.to_csv(caminho_csv, index=False)

    print(f"ID_MMA_COMPLETO preenchido com sucesso!\n{caminho_csv}")