"""
stats.py

Computes every named number used inline in book_master.docx.
Each function handles one topic and returns a dict of {TOKEN: value}.
compute_stats() merges them all into the single dict fill_inline_stats() needs.

Splitting by topic (instead of one giant function) makes it easy to:
  - test/debug one group of numbers at a time
  - see at a glance which numbers come from which calculation
  - add a new topic without touching existing ones
"""

import pandas as pd

def _load_stations() -> pd.DataFrame:
    """Loads the monitoring stations dataset (one row per station/pollutant/
    period -- NOT deduped here, since a station's row that matches a given
    year can differ from the row that would be kept by an early dedupe)."""
    df = pd.read_csv(f"https://arquivos.lcqar.ufsc.br/data/databases/stations/Monitoramento_QAr_BR.csv")
    return df


def _monitored_in(df: pd.DataFrame, year: int) -> pd.Series:
    """ANOS_MONITORADOS holds a comma-separated list of years per station
    (e.g. '2019,2020,2021'), not a single year, so we check membership."""
    return df["ANOS_MONITORADOS"].str.split(",").apply(
        lambda years: isinstance(years, list) and str(year) in years
    )


def _normalize_uf(uf: str | None) -> str | None:
    """"BRASIL" (ou None/""/"BR"/"TODOS") => sem filtro, Brasil inteiro
    (comportamento atual). Uma sigla real (ex: "SC") => filtra por estado."""
    if uf in (None, "", "BRASIL", "BR", "TODOS"):
        return None
    return uf


def _stations_in_year(df: pd.DataFrame, year: int, uf: str | None = None) -> pd.DataFrame:
    """Filters rows monitored in `year` (e, se `uf` for passado, também por
    estado) FIRST, then dedupes by station (ID_OEMA) -- deduping before
    filtering would arbitrarily keep just one of a station's several
    pollutant/period rows, possibly discarding the very row that matched
    the requested year."""
    mask = _monitored_in(df, year)
    if uf is not None:
        mask = mask & (df["UF"] == uf)
    return df[mask].drop_duplicates(subset=["ID_OEMA"])


def _is_nao_informado(categoria: pd.Series) -> pd.Series:
    """CATEGORIA marks 'not informed' both as real NaN and as the literal
    string 'Nao declarado' -- isna() alone misses the latter."""
    return categoria.isna() | (categoria == "Nao declarado")


def stats_contagem_geral(current_year: int, previous_year: int, uf: str | None = None) -> dict:
    df = _load_stations()
    uf = _normalize_uf(uf)

    """Numbers about total station counts and method breakdown."""
    cur_mask = _monitored_in(df, current_year)
    prev_mask = _monitored_in(df, previous_year)
    if uf is not None:
        cur_mask = cur_mask & (df["UF"] == uf)
        prev_mask = prev_mask & (df["UF"] == uf)
    if not cur_mask.any() or not prev_mask.any():
        raise ValueError(f"Data for year {current_year} or {previous_year} not found in the dataset.")

    cur = _stations_in_year(df, current_year, uf)
    prev = _stations_in_year(df, previous_year, uf)

    n_total_cur = len(cur)
    n_total_prev = len(prev)

    n_ref_cur = (cur["CATEGORIA"] == "Referencia").sum()
    n_ref_prev = (prev["CATEGORIA"] == "Referencia").sum()

    n_ind_cur = (cur["CATEGORIA"] == "Indicativa").sum()
    n_ind_prev = (prev["CATEGORIA"] == "Indicativa").sum()

    n_metodo_nao_informado = _is_nao_informado(cur["CATEGORIA"]).sum()

    return {
        f"N_TOTAL_{current_year}": n_total_cur,
        f"N_AUMENTO_TOTAL_{current_year}": n_total_cur - n_total_prev,
        f"ANO_BASE_ANTERIOR_{previous_year}": previous_year,
        f"N_REFERENCIA_{current_year}": n_ref_cur,
        f"N_REDUCAO_REFERENCIA_{current_year}_{previous_year}": n_ref_cur - n_ref_prev,
        f"N_INDICATIVA_{current_year}": n_ind_cur,
        f"N_AUMENTO_INDICATIVA_{current_year}_{previous_year}": n_ind_cur - n_ind_prev,
        f"N_METODO_NAO_INFORMADO_{current_year}": n_metodo_nao_informado,
    }


def stats_status_funcionamento(current_year: int, uf: str | None = None) -> dict:
    df = _load_stations()
    uf = _normalize_uf(uf)
    """Numbers about active/inactive station status, broken down by method."""
    cur = _stations_in_year(df, current_year, uf)
    ref = cur[cur["CATEGORIA"] == "Referencia"]
    ind = cur[cur["CATEGORIA"] == "Indicativa"]
    nc = cur[_is_nao_informado(cur["CATEGORIA"])]


    return {
        f"{current_year}": current_year,
        f"N_TOTAL_ATIVAS_{current_year}": (cur["STATUS"] == "Ativa").sum(),
        f"N_TOTAL_INATIVAS_{current_year}": (cur["STATUS"] == "Inativa").sum(),
        f"N_TOTAL_SEM_STATUS_{current_year}": cur["STATUS"].isna().sum(),
        f"N_REF_ATIVAS_{current_year}": (ref["STATUS"] == "Ativa").sum(),
        f"N_REF_INATIVAS_{current_year}": (ref["STATUS"] == "Inativa").sum(),
        f"N_REF_SEM_STATUS_{current_year}": ref["STATUS"].isna().sum(),
        f"N_IND_ATIVAS_{current_year}": (ind["STATUS"] == "Ativa").sum(),
        f"N_IND_INATIVAS_{current_year}": (ind["STATUS"] == "Inativa").sum(),
        f"N_IND_SEM_STATUS_{current_year}": ind["STATUS"].isna().sum(),
        f"N_NC_ATIVAS_{current_year}": (nc["STATUS"] == "Ativa").sum(),
        f"N_NC_INATIVAS_{current_year}": (nc["STATUS"] == "Inativa").sum(),
        f"N_NC_SEM_STATUS_{current_year}": nc["STATUS"].isna().sum(),
    }


def compute_stats(uf: str | None = None) -> dict:
    """Merges every topic's numbers into one dict for fill_inline_stats().

    uf: sigla do estado (ex: "SC"), ou "BRASIL"/None para o país inteiro
    (comportamento padrão, sem filtro)."""
    uf = _normalize_uf(uf)
    current_year, previous_year = 2024, 2023

    stats = {"current_year": current_year, "previous_year": previous_year}
    if uf is not None:
        stats["UF"] = uf
    stats.update(stats_contagem_geral(current_year, previous_year, uf))
    stats.update(stats_status_funcionamento(current_year, uf))
    # Add more stats_xxx() calls here as you add more sections with inline numbers.

    return stats


if __name__ == "__main__":
    # Quick sanity check: run this file directly to print all computed
    # numbers before wiring it into the full book build, so you can catch
    # bad data or logic errors early. Ex: python compute_stats.py SP
    import sys
    uf_teste = sys.argv[1] if len(sys.argv) > 1 else None
    for key, value in compute_stats(uf_teste).items():
        print(f"{key}: {value}")
