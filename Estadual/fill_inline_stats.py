"""
fill_inline_stats.py

Fills {{TOKEN}} markers that sit INSIDE normal sentences (not markers
alone on their own line -- that's what fill_book.py's table/image markers
are for). This is for narrative text like:

    "foram contabilizadas {{N_TOTAL_2024}} estacoes..."

HOW TO USE
----------
1. Write a Python function that computes your numbers and returns a dict:

       def compute_stats():
           return {
               "N_TOTAL_2024": 562,
               "N_AUMENTO_TOTAL": 83,
               "ANO_BASE_ANTERIOR": 2023,
               ...
           }

   Put this in stats.py (or wherever your other item scripts live).

2. In book_master.docx, write your paragraphs normally, with {{TOKEN}}
   dropped inline wherever a number goes.

3. Call fill_inline_stats(doc, stats_dict) as part of the build pipeline,
   BEFORE fill_book() runs its table/image marker pass (order doesn't
   actually matter, they don't conflict -- inline markers are text inside
   a sentence, marker-alone paragraphs are the whole paragraph).

NOTE ON FORMATTING
------------------
Word splits paragraph text across multiple hidden "runs" (chunks with
their own formatting) even when it looks like one continuous sentence.
To reliably replace text that might be split across those runs, this
function rebuilds the paragraph's text as a single run when any token
inside it gets replaced. Practically: bold/italic/color applied to the
WHOLE paragraph is preserved; formatting applied to only PART of a
paragraph (e.g. just one bolded word in the middle of a sentence) is not
guaranteed to survive if a token sits near it. For narrative paragraphs
of plain text (the normal case), this is not an issue.
"""

import re

TOKEN_RE = re.compile(r"\{\{([A-Za-z0-9_]+)\}\}")


def fill_inline_stats(doc, stats: dict):
    filled_tokens = set()
    missing_tokens = set()

    for paragraph in doc.paragraphs:
        text = paragraph.text
        tokens_in_paragraph = TOKEN_RE.findall(text)
        if not tokens_in_paragraph:
            continue

        # Skip paragraphs that are ONLY a marker (those belong to
        # fill_book.py's table/image logic, not this one).
        if text.strip().startswith("{{") and text.strip().endswith("}}") \
                and len(tokens_in_paragraph) == 1:
            continue

        new_text = text
        for token in tokens_in_paragraph:
            if token in stats:
                new_text = new_text.replace(f"{{{{{token}}}}}", str(stats[token]))
                filled_tokens.add(token)
            else:
                missing_tokens.add(token)

        if new_text != text:
            # Rebuild the paragraph as a single run with the replaced text,
            # keeping the first run's character formatting (font, bold, etc.)
            # and the paragraph's own style (heading level, alignment, etc.)
            first_run = paragraph.runs[0] if paragraph.runs else None
            for run in list(paragraph.runs):
                run.text = ""
            if paragraph.runs:
                paragraph.runs[0].text = new_text
            else:
                paragraph.add_run(new_text)

    return filled_tokens, missing_tokens


if __name__ == "__main__":
    import sys
    from docx import Document

    if len(sys.argv) != 3:
        print("Usage: python fill_inline_stats.py <book_master.docx> <output.docx>")
        sys.exit(1)

    # Demo stats matching the example paragraph -- replace with your
    # real compute_stats() function.
    demo_stats = {
        "N_TOTAL_2024": 562,
        "N_AUMENTO_TOTAL": 83,
        "ANO_BASE_ANTERIOR": 2023,
        "N_REFERENCIA": 359,
        "N_REDUCAO_REFERENCIA": 17,
        "N_INDICATIVA": 194,
        "N_AUMENTO_INDICATIVA": 100,
        "N_METODO_NAO_INFORMADO": 9,
        "N_REF_ATIVAS": 279,
        "N_REF_INATIVAS": 68,
        "N_REF_SEM_STATUS": 11,
    }

    doc = Document(sys.argv[1])
    filled, missing = fill_inline_stats(doc, demo_stats)
    doc.save(sys.argv[2])

    print(f"Filled: {sorted(filled)}")
    if missing:
        print(f"Missing (no matching stat): {sorted(missing)}")
    print(f"Saved: {sys.argv[2]}")
