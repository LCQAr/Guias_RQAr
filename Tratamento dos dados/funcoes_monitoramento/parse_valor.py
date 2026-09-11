import pandas as pd
def parse_valor(x):
    """
    Remove espaços em branco e converte valores escritos
    com vírgula decimal para o formato numérico do Python.
    """

    if pd.isna(x):
        return x

    x = str(x).strip()

    if x == "":
        return None

    if "," in x:
        x = x.replace(".", "")
        x = x.replace(",", ".")

    return float(x)