"""
dashboard.py

Painel interativo que reaproveita DIRETAMENTE o build_book.py -- a mesma
lista NOTEBOOKS, a mesma função run_notebook() (papermill + --cwd),
o mesmo mecanismo de injeção de UF. Nada é reimplementado ou duplicado.

A diferença: em vez de converter o resultado em imagem estática para o
Word (como o build_book.py faz), este painel mostra o HTML de cada
seção AO VIVO na tela -- mapas e tabelas continuam clicáveis/interativos,
diferente do relatório final.

COMO ABRIR
----------
    streamlit run dashboard.py
"""

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

import build_book  # reaproveita NOTEBOOKS, run_notebook, HERE -- fonte única

st.set_page_config(page_title="Painel RQAr — Exploração", layout="wide")

UFS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO",
]

st.sidebar.title("Filtros")
uf_selecionada = st.sidebar.selectbox("Estado (UF)", UFS)
secao_selecionada = st.sidebar.selectbox("Seção", build_book.NOTEBOOKS)
rodar = st.sidebar.button("▶ Gerar / Atualizar", use_container_width=True)

st.title(f"Painel interativo — {secao_selecionada}")
st.caption(f"Estado selecionado: {uf_selecionada}")

notebook_path = build_book.HERE / secao_selecionada
outputs_dir = notebook_path.parent / "outputs"

if rodar:
    with st.spinner(f"Rodando {notebook_path.name} para {uf_selecionada}... isso usa exatamente o mesmo código do relatório."):
        try:
            build_book.run_notebook(notebook_path)
            st.success("Concluído!")
        except Exception as e:
            st.error(f"Erro ao rodar esta seção: {e}")

if outputs_dir.exists():
    html_files = sorted(outputs_dir.glob("*.html"))
    if not html_files:
        st.info("Ainda não há resultado gerado para esta seção. Clique em 'Gerar / Atualizar'.")
    for html_file in html_files:
        st.subheader(html_file.stem)
        html_content = html_file.read_text(encoding="utf-8")
        components.html(html_content, height=600, scrolling=True)
else:
    st.info("Ainda não há resultado gerado para esta seção. Clique em 'Gerar / Atualizar'.")
