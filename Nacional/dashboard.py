"""
dashboard.py

Painel interativo que reaproveita DIRETAMENTE o build_book.py -- a mesma
lista NOTEBOOKS, a mesma função run_notebook() (papermill + --cwd),
o mesmo mecanismo de injeção de UF.

Igual ao painel do Estadual, mas com "BRASIL" (país inteiro, sem filtro)
como opção padrão no seletor de estado -- basta escolher uma UF para ver
a mesma seção filtrada para aquele estado.

COMO ABRIR
----------
    streamlit run dashboard.py
"""

from pathlib import Path
import pandas as pd
import re

import streamlit as st
import streamlit.components.v1 as components

import build_book

st.set_page_config(page_title="Painel Interativo RQAr", page_icon="🌎", layout="wide")

TITULO_OFICIAL = "Painel de Dados - Relatório Anual de Acompanhamento da Qualidade do Ar"

# --------------------------------------------------------------------------
# LOGO: coloque o arquivo de imagem na raiz do projeto (junto deste
# dashboard.py) e escreva o nome do arquivo aqui. Deixe "" para não
# mostrar nenhum logo.
# --------------------------------------------------------------------------
LOGO_PATH = "logoGuiaRQAr.png"

# "BRASIL" primeiro = padrão do seletor = país inteiro, sem filtro por UF.
UFS = [
    "BRASIL",
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO",
]


def rotulo_uf(uf: str) -> str:
    return "Brasil (todos os estados)" if uf == "BRASIL" else uf


DESCRICOES_METRICAS = [
    (re.compile(r"^current_year$"), "Ano de referência do relatório"),
    (re.compile(r"^previous_year$"), "Ano do relatório anterior"),
    (re.compile(r"^UF$"), "Estado selecionado"),
    (re.compile(r"^N_TOTAL_(\d{4})$"), "Total de estações"),
    (re.compile(r"^N_TOTAL_ATIVAS_(\d{4})$"), "Total de estações ativas"),
    (re.compile(r"^N_TOTAL_INATIVAS_(\d{4})$"), "Total de estações inativas"),
    (re.compile(r"^N_TOTAL_SEM_STATUS_(\d{4})$"), "Total de estações sem status informado"),
    (re.compile(r"^N_AUMENTO_TOTAL_(\d{4})$"), "Aumento no total de estações em relação ao ano anterior"),
    (re.compile(r"^N_REFERENCIA_(\d{4})$"), "Estações de referência"),
    (re.compile(r"^N_REF_ATIVAS_(\d{4})$"), "Estações de referência ativas"),
    (re.compile(r"^N_REF_INATIVAS_(\d{4})$"), "Estações de referência inativas"),
    (re.compile(r"^N_REF_SEM_STATUS_(\d{4})$"), "Estações de referência sem status"),
    (re.compile(r"^N_REDUCAO_REFERENCIA_(\d{4})_(\d{4})$"), "Redução de estações de referência entre {1} e {0}"),
    (re.compile(r"^N_INDICATIVA_(\d{4})$"), "Estações indicativas"),
    (re.compile(r"^N_IND_ATIVAS_(\d{4})$"), "Estações indicativas ativas"),
    (re.compile(r"^N_IND_INATIVAS_(\d{4})$"), "Estações indicativas inativas"),
    (re.compile(r"^N_IND_SEM_STATUS_(\d{4})$"), "Estações indicativas sem status"),
    (re.compile(r"^N_AUMENTO_INDICATIVA_(\d{4})_(\d{4})$"), "Aumento de estações indicativas entre {1} e {0}"),
    (re.compile(r"^N_METODO_NAO_INFORMADO_(\d{4})$"), "Estações sem categoria informado"),
    (re.compile(r"^N_NC_ATIVAS_(\d{4})$"), "Estações sem categoria declarada, ativas"),
    (re.compile(r"^N_NC_INATIVAS_(\d{4})$"), "Estações sem categoria declarada, inativas"),
    (re.compile(r"^N_NC_SEM_STATUS_(\d{4})$"), "Estações sem categoria declarada, sem status"),
]


def descricao_metrica(chave: str) -> str:
    for padrao, template in DESCRICOES_METRICAS:
        m = padrao.match(chave)
        if m:
            try:
                return template.format(*m.groups())
            except (IndexError, KeyError):
                return template  # template não tinha {} suficientes -- mostra como está
    return "—"

# --------------------------------------------------------------------------
# Scripts "auxiliares" -- não têm outputs/*.html para mostrar (preparam
# dados para outras seções). Nenhum notebook de build_book.NOTEBOOKS se
# encaixa nisso hoje no Nacional; ajuste aqui se algum for adicionado.
# --------------------------------------------------------------------------
SEM_VISUALIZACAO = set()

# Seções que dependem de scripts auxiliares rodando antes. Vazio por
# enquanto -- mesma estrutura do Estadual, para consistência futura.
DEPENDENCIAS = {}

# CSS injetado em todo HTML mostrado, para gráficos/tabelas ocuparem a
# largura inteira do painel em vez de ficarem espremidos à esquerda.
CSS_LARGURA_TOTAL = """
<style>
  html, body { margin:0; padding:0; width:100% !important; }
  table { width:100% !important; }
  iframe, div, svg, img { max-width:100% !important; }
</style>
"""

if "ultimo_gerado" not in st.session_state:
    # chave = pasta outputs/ (compartilhada entre notebooks da mesma seção),
    # valor = (notebook, uf) que está atualmente ali dentro. Como vários
    # notebooks podem compartilhar a MESMA pasta outputs/, rastrear por
    # pasta (não por notebook) é o que garante detectar corretamente
    # quando o conteúdo foi sobrescrito por outro notebook da mesma seção.
    st.session_state.ultimo_gerado = {}

if LOGO_PATH and (build_book.HERE / LOGO_PATH).exists():
    st.sidebar.image(str(build_book.HERE / LOGO_PATH), width=300)

st.sidebar.title("Filtros")
uf_selecionada = st.sidebar.selectbox("Estado (UF)", UFS, format_func=rotulo_uf)
secao_selecionada = st.sidebar.selectbox("Seção", build_book.NOTEBOOKS)
altura_frame = st.sidebar.slider("Altura do gráfico/tabela", 400, 1600, 900, step=100)
rodar = st.sidebar.button("▶️ Gerar / Atualizar")

st.title(TITULO_OFICIAL)
st.caption(f"Estado selecionado: {rotulo_uf(uf_selecionada)}")

tab_secoes, tab_metricas = st.tabs(["Seções interativas", "Métricas"])

notebook_path = build_book.HERE / secao_selecionada
outputs_dir = notebook_path.parent / "outputs"
outputs_key = str(outputs_dir)


def limpar_outputs(pasta: Path):
    if pasta.exists():
        for old_file in pasta.glob("*.html"):
            old_file.unlink()


def rodar_notebook_com_dependencias(caminho_notebook: str, uf: str):
    dependencias = DEPENDENCIAS.get(caminho_notebook, [])
    if dependencias:
        st.info(
            f"Esta seção depende de {len(dependencias)} script(s) de preparação "
            f"sem visualização própria. Isso pode levar mais tempo que o normal."
        )
        for dep in dependencias:
            dep_path = build_book.HERE / dep
            with st.spinner(f"Preparando dados: {Path(dep).name} (sem visualização, só roda em segundo plano)..."):
                build_book.run_notebook(dep_path, parameters={"UF": uf})

    nb_path = build_book.HERE / caminho_notebook
    nb_outputs_dir = nb_path.parent / "outputs"
    limpar_outputs(nb_outputs_dir)

    with st.spinner(f"Rodando {nb_path.name} para {rotulo_uf(uf)}..."):
        build_book.run_notebook(nb_path, parameters={"UF": uf})
    st.session_state.ultimo_gerado[str(nb_outputs_dir)] = (caminho_notebook, uf)

with tab_secoes:
    st.subheader(secao_selecionada)

    # --- Seção sem visualização própria: mensagem dedicada, sem tentar exibir HTML ---
    if secao_selecionada in SEM_VISUALIZACAO:
        st.info(
            "Nota: Este script não tem visualização própria — ele prepara dados usados "
            "por outras seções. Rode-o aqui apenas se quiser atualizar esses dados "
            "manualmente. Pode demorar mais que o normal."
        )
        if rodar:
            with st.spinner(f"Rodando {notebook_path.name} para {rotulo_uf(uf_selecionada)}... sem visualização disponível."):
                try:
                    build_book.run_notebook(notebook_path, parameters={"UF": uf_selecionada})
                    st.success("Concluído! (sem visualização para mostrar)")
                except Exception as e:
                    st.error(f"Erro ao rodar: {e}")

    else:
        if rodar:
            try:
                rodar_notebook_com_dependencias(secao_selecionada, uf_selecionada)
                st.success("Concluído!")
            except Exception as e:
                st.error(f"Erro ao rodar esta seção: {e}")
                st.session_state.ultimo_gerado.pop(outputs_key, None)

        gerado = st.session_state.ultimo_gerado.get(outputs_key)

        if gerado is None:
            st.info("Alerta: Ainda não foi gerado nada nesta sessão para esta seção. Clique em 'Gerar / Atualizar'.")
        elif gerado != (secao_selecionada, uf_selecionada):
            gerado_secao, gerado_uf = gerado
            st.warning(
                f"O conteúdo atual desta pasta de saída foi gerado por **{Path(gerado_secao).name}** "
                f"para **{rotulo_uf(gerado_uf)}** — não bate com a seção/estado selecionados agora "
                f"({Path(secao_selecionada).name} / {rotulo_uf(uf_selecionada)}). "
                f"Clique em 'Gerar / Atualizar' para gerar o que está selecionado."
            )
        elif outputs_dir.exists():
            html_files = sorted(outputs_dir.glob("*.html"))
            if not html_files:
                st.info("Alerta: Nenhum arquivo de saída encontrado para esta seção.")
            for html_file in html_files:
                st.subheader(html_file.stem)
                html_content = html_file.read_text(encoding="utf-8")
                components.html(CSS_LARGURA_TOTAL + html_content, height=altura_frame, scrolling=True)

with tab_metricas:
    st.subheader(f"Métricas calculadas — {rotulo_uf(uf_selecionada)}")
    st.caption("Mesmos números usados no relatório (compute_stats.py), calculados para o estado selecionado (ou Brasil inteiro).")

    calcular = st.button("Calcular métricas", key="calcular_metricas")

    if calcular:
        from scripts import compute_stats as stats_module
        with st.spinner(f"Calculando estatísticas para {rotulo_uf(uf_selecionada)}..."):
            try:
                st.session_state["metricas"] = stats_module.compute_stats(uf_selecionada)
                st.session_state["metricas_uf"] = uf_selecionada
            except Exception as e:
                st.session_state.pop("metricas", None)
                st.error(f"Não foi possível calcular métricas para {rotulo_uf(uf_selecionada)}: {e}")

    metricas = st.session_state.get("metricas")
    metricas_uf = st.session_state.get("metricas_uf")

    if metricas is None:
        st.info("Clique em 'Calcular métricas' para ver os números deste estado.")
    elif metricas_uf != uf_selecionada:
        st.warning(
            f"As métricas mostradas são de **{rotulo_uf(metricas_uf)}** — clique em "
            f"'Calcular métricas' para atualizar para **{rotulo_uf(uf_selecionada)}**."
        )
    else:
        # Números-chave em destaque
        col1, col2, col3, col4 = st.columns(4)
        ano = metricas.get("current_year", "")
        col1.metric(f"Total de estações ({ano})", metricas.get(f"N_TOTAL_{ano}", "—"))
        col2.metric("Ativas", metricas.get(f"N_TOTAL_ATIVAS_{ano}", "—"))
        col3.metric("Inativas", metricas.get(f"N_TOTAL_INATIVAS_{ano}", "—"))
        col4.metric("Sem status", metricas.get(f"N_TOTAL_SEM_STATUS_{ano}", "—"))

        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(f"Total de estações de Referência ({ano})", metricas.get(f"N_REFERENCIA_{ano}", "—"))
        col2.metric("Ativas", metricas.get(f"N_REF_ATIVAS_{ano}", "—"))
        col3.metric("Inativas", metricas.get(f"N_REF_INATIVAS_{ano}", "—"))
        col4.metric("Sem status", metricas.get(f"N_REF_SEM_STATUS_{ano}", "—"))

        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(f"Total de estações Indicativas ({ano})", metricas.get(f"N_INDICATIVA_{ano}", "—"))
        col2.metric("Ativas", metricas.get(f"N_IND_ATIVAS_{ano}", "—"))
        col3.metric("Inativas", metricas.get(f"N_IND_INATIVAS_{ano}", "—"))
        col4.metric("Sem status", metricas.get(f"N_IND_SEM_STATUS_{ano}", "—"))

        st.divider()
        st.caption(f"Todos os valores calculados: {ano}")
        tabela_metricas = pd.DataFrame(
            [{"Métrica": k, "Descrição": descricao_metrica(k), "Valor": v} for k, v in metricas.items()]
        )
        st.dataframe(tabela_metricas, hide_index=True)
