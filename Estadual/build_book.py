"""
build_book.py

Fully automated pipeline. No screenshots taken by a human at any point --
Playwright renders each HTML output in an invisible browser and captures it.

For each notebook (e.g. secao_3/secao_3.1.ipynb):
  1. Runs it headlessly with its real code (jupyter nbconvert --execute).
     This regenerates that notebook's outputs/*.html files (tables, maps)
     exactly as it does today when you run it by hand.
  2. Every outputs/*.html the notebook produced gets rendered in headless
     Chromium and saved as a PNG.
  3. Each PNG is matched to a marker in book_master.docx by name
     (outputs/tabela6.html -> {{TABELA_6}}, outputs/figura23.html -> {{FIGURA_23}})
     and inserted in place of that marker.
  4. The final book is exported as .docx and .pdf.

Re-running this is the entire "yearly refresh": new data in the source
CSVs -> new numbers in the tables/maps -> new book, automatically.

USAGE
-----
    python build_book.py

One-time setup (technical person, once per machine):
    pip install -r requirements.txt
    playwright install chromium
"""

import os
import subprocess
import sys
from pathlib import Path

from docx import Document

sys.path.insert(0, str(Path(__file__).parent))
from fill_book import fill_book
from fill_inline_stats import fill_inline_stats
from html_to_image import html_to_png
from scripts.compute_stats import compute_stats

HERE = Path(__file__).parent
MASTER = HERE / "book_master.docx"
MASTER_WITH_STATS = HERE / "book_master_with_stats.docx"  # intermediate file, auto-generated
CONTENT_DIR = HERE / "content"
OUTPUT_DOCX = HERE / "output" / "book_filled.docx"
OUTPUT_PDF = HERE / "output" / "book_filled.pdf"

# --------------------------------------------------------------------------
# ÚNICO LUGAR a editar para mudar valores usados por vários notebooks
# (ex: qual estado processar). Cada notebook só recebe um valor daqui se
# tiver uma célula marcada com a tag "parameters" -- veja o Guia, Seção 7.
# --------------------------------------------------------------------------
PARAMETERS = {
    # O painel gráfico pode sobrescrever isto por seleção do usuário (variável
    # de ambiente GUIA_UF). Rodando por terminal sem o painel, usa "SC" abaixo.
    "UF": os.environ.get("GUIA_UF", "SC"),
}

# Each notebook, e o prefixo do marcador para seus outputs.
# outputs/<name>.html dentro da pasta do notebook vira {{<MARKER_PREFIX>_<NAME>}}
#
# NOTA: só arquivos .ipynb entram aqui -- o papermill executa notebooks,
# não scripts .py comuns. compute_stats.py NÃO entra nesta lista; ele é
# chamado diretamente como função Python (compute_stats(...)), mais abaixo.
NOTEBOOKS = [
    "scripts/seasonality_analisys.ipynb",
    "scripts/trend_analisys.ipynb",
    "secao_3/secao_03.ipynb",
    "secao_3/secao_3.1.ipynb",
    #"secao_3/secao_3.2.ipynb",
    #"secao_3/secao_3.3.ipynb",
    #"secao_3/secao_3.4.ipynb",
    #"secao_3/secao_3.5.ipynb",
    #"secao_3/secao_3.6.1.ipynb",
    #"secao_3/secao_3.6.2.ipynb",
    #"secao_3/secao_3.6.3.ipynb",
    #"secao_3/secao_3.6.4.ipynb",
]


def run_notebook(notebook_path: Path, parameters: dict | None = None):
    """Executes a notebook in place, headlessly, using its real code.

    Runs papermill as a SEPARATE OS PROCESS (via its command-line interface),
    not as an in-process Python API call. This matters for memory: calling
    papermill.execute_notebook() directly runs the Jupyter kernel inside
    this same long-lived build_book.py process, and if a notebook errors
    out, that kernel can be left running in the background (a known
    papermill/nbclient issue) -- these leaks accumulate silently over
    multiple notebooks/runs. Running papermill as its own subprocess means
    the operating system fully reclaims everything that process (and any
    kernel it spawned) used, the moment it exits -- success or failure.

    --cwd matches nbconvert's old default of running each notebook from
    inside its own folder -- required for notebooks that do bare imports
    like `import flagTables` (a file living alongside the notebook, not
    at the project root)."""
    python_exe = sys.executable
    # pythonw.exe (Windows, no console window) breaks papermill/tqdm, which
    # need a real console to write progress output to. If build_book.py
    # itself happens to be running under pythonw.exe (e.g. launched via
    # painel.py), swap to the sibling python.exe for this subprocess call.
    if python_exe.lower().endswith("pythonw.exe"):
        candidato = python_exe[: -len("pythonw.exe")] + "python.exe"
        if Path(candidato).exists():
            python_exe = candidato

    cmd = [
        python_exe, "-m", "papermill",
        str(notebook_path), str(notebook_path),
        "--kernel", "python3",
        "--cwd", str(notebook_path.parent),
    ]
    for key, value in (parameters or {}).items():
        cmd += ["-p", key, str(value)]
    subprocess.run(cmd, check=True)


def marker_name_for(notebook_path: Path, html_file: Path) -> str:
    # secao_3/secao_3.1.ipynb + outputs/tabela6.html -> SECAO_3_1_TABELA6
    section_tag = notebook_path.stem.upper().replace(".", "_").replace("-", "_")
    item_tag = html_file.stem.upper()
    return f"{section_tag}_{item_tag}"


def process_notebook(notebook_path: Path):
    notebook_path = HERE / notebook_path
    outputs_dir = notebook_path.parent / "outputs"

    # outputs/ é compartilhada por TODOS os notebooks da mesma pasta de
    # seção (ex: secao_3.1, secao_3.2... todos escrevem em secao_3/outputs/).
    # Limpar antes de rodar evita pegar arquivo velho de outro notebook ou
    # de uma execução anterior (para outro estado) por engano.
    if outputs_dir.exists():
        for old_file in outputs_dir.glob("*.html"):
            old_file.unlink()

    print(f"Running {notebook_path.name} ...")
    run_notebook(notebook_path, parameters=PARAMETERS)

    if not outputs_dir.exists():
        print(f"  (no outputs/ folder found for {notebook_path.name}, skipping)")
        return

    for html_file in outputs_dir.glob("*.html"):
        marker = marker_name_for(notebook_path, html_file)
        png_path = CONTENT_DIR / f"{marker}.png"
        html_to_png(html_file, png_path)
        print(f"  {html_file.name} -> {{{{{marker}}}}} ({png_path.name})")


def convert_to_pdf(docx_path: Path, pdf_path: Path):
    try:
        from docx2pdf import convert
        convert(str(docx_path), str(pdf_path))
        print(f"PDF created (via Word): {pdf_path.name}")
        return
    except Exception as e:
        print(f"docx2pdf unavailable ({e}), trying LibreOffice...")
    try:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf",
             "--outdir", str(pdf_path.parent), str(docx_path)],
            check=True, capture_output=True,
        )
        print(f"PDF created (via LibreOffice): {pdf_path.name}")
    except Exception as e:
        print(f"Could not auto-create PDF ({e}). Open the .docx and Save As PDF.")


if __name__ == "__main__":
    CONTENT_DIR.mkdir(exist_ok=True)
    OUTPUT_DOCX.parent.mkdir(exist_ok=True)

    for nb in NOTEBOOKS:
        nb_path = HERE / nb
        if not nb_path.exists():
            print(f"Skipping {nb} (not found)")
            continue
        process_notebook(Path(nb))

    print("\nComputing inline stats...")
    doc = Document(str(MASTER))
    filled, missing = fill_inline_stats(doc, compute_stats(PARAMETERS["UF"]))
    print(f"  Filled {len(filled)} inline number(s): {sorted(filled)}")
    if missing:
        print(f"  WARNING: no data found for {sorted(missing)} -- these {{...}} were left as-is in the text")
    doc.save(str(MASTER_WITH_STATS))

    print("\nRebuilding book from master...")
    fill_book(str(MASTER_WITH_STATS), str(CONTENT_DIR), str(OUTPUT_DOCX))

    print("Creating PDF...")
    convert_to_pdf(OUTPUT_DOCX, OUTPUT_PDF)

    print("\nDone! Check the 'output' folder.")
