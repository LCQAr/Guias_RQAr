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
import psutil
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
# tiver uma célula marcada com a tag "parameters".
# --------------------------------------------------------------------------
PARAMETERS = {
    # "BRASIL" = sem filtro, país inteiro (padrão do livro). A dashboard pode
    # sobrescrever isto por seleção do usuário (variável de ambiente GUIA_UF).
    "UF": os.environ.get("GUIA_UF", "BRASIL"),
}

# Each notebook, and the marker prefix its outputs should map to.
# outputs/<name>.html inside that notebook's folder becomes {{<MARKER_PREFIX>_<NAME>}}
# Descomentar notebooks que você não quer rodar (e.g. seções incompletas).
NOTEBOOKS = [
    "secao_1/secao_1.2.ipynb",
    "secao_3/secao_03.ipynb",
    # "secao_3/secao_3.1.ipynb",
    # "secao_3/secao_3.2.ipynb",
    # "secao_3/secao_3.3.ipynb",
    # "secao_3/secao_3.4.ipynb",
    # "secao_3/secao_3.5.ipynb",
    # "secao_3/secao_3.6.1.ipynb",
    # "secao_3/secao_3.6.2.ipynb",
    # "secao_3/secao_3.6.3.ipynb",
    # "secao_3/secao_3.6.4.ipynb",
    #"secao_4/secao_4.1.1.ipynb",
    #"secao_4/secao_4.1.2.ipynb",
    #"secao_4/secao_4.2.ipynb",
    #"secao_4/secao_4.3.ipynb",
    #"secao_4/secao_4.4.1.ipynb",
    #"secao_4/secao_4.4.2.ipynb",
]


MEMORY_WARN_PERCENT = 85  # ask before continuing once system memory usage crosses this


def check_memory(step_label: str, threshold_percent: float = MEMORY_WARN_PERCENT):
    """Prints current memory usage and, if it's high, blocks until the user
    confirms whether to keep going. Notebook execution (nbconvert) and HTML
    screenshotting (Playwright) are the steps most likely to balloon memory,
    so this is called after each of those instead of running unattended."""
    vm = psutil.virtual_memory()
    proc_mb = psutil.Process().memory_info().rss / (1024 ** 2)
    print(f"  [memory] after {step_label}: system {vm.percent:.0f}% used "
          f"({vm.available / (1024 ** 3):.1f} GB free) | this process: {proc_mb:.0f} MB")

    if vm.percent >= threshold_percent:
        answer = input(
            f"  Memory usage is high ({vm.percent:.0f}% >= {threshold_percent}%). "
            "Continue running build_book.py? [y/N] "
        ).strip().lower()
        if answer != "y":
            print("Stopping build at user's request (high memory usage).")
            sys.exit(1)


def run_notebook(notebook_path: Path, parameters: dict | None = None):
    """Executes a notebook in place, headlessly, using its real code.

    Runs papermill as a SEPARATE OS PROCESS (via its command-line interface),
    not as an in-process Python API call -- see Estadual/build_book.py para o
    raciocínio completo (isolamento de memória/kernel).

    --cwd roda cada notebook a partir da sua própria pasta -- necessário para
    notebooks que fazem import direto de arquivos vizinhos (ex: flagTables.py)."""
    python_exe = sys.executable
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
    # seção. Limpar antes de rodar evita pegar arquivo velho de outro
    # notebook ou de uma execução anterior (para outro estado) por engano.
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
        check_memory(f"processing {nb}")

    print("\nComputing inline stats...")
    doc = Document(str(MASTER))
    filled, missing = fill_inline_stats(doc, compute_stats(PARAMETERS["UF"]))
    print(f"  Filled {len(filled)} inline number(s): {sorted(filled)}")
    if missing:
        print(f"  WARNING: no data found for {sorted(missing)} -- these {{...}} were left as-is in the text")
    doc.save(str(MASTER_WITH_STATS))

    print("\nRebuilding book from master...")
    fill_book(str(MASTER_WITH_STATS), str(CONTENT_DIR), str(OUTPUT_DOCX))
    check_memory("assembling final .docx")

    print("Creating PDF...")

    # Descomentar a linha abaixo se você quiser gerar o PDF automaticamente. 
    # Caso contrário, abra o arquivo .docx e salve como PDF manualmente.
    #convert_to_pdf(OUTPUT_DOCX, OUTPUT_PDF)

    print("\nDone! Check the 'output' folder.")