#!/usr/bin/env python3
"""
convert_to_md.py
================
Convertit les ressources téléchargées (PDF / HTML) en fichiers Markdown.

Technologies :
- PDF → Markdown via Docling (avec OCR désactivé pour la performance)
- HTML → Markdown via markdownify

Usage :
    uv run python convert_to_md.py
    # ou si .venv activé :
    python convert_to_md.py
"""

import sys
import time
from pathlib import Path

from markdownify import markdownify as mdify

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent
DOWNLOADS_DIR = REPO_ROOT / "downloads"
MARKDOWN_DIR = REPO_ROOT / "markdown"


def get_docling_converter():
    """Construit le convertisseur Docling avec OCR désactivé."""
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend

    opts = PdfPipelineOptions()
    opts.do_ocr = False
    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=opts,
                backend=PyPdfiumDocumentBackend,
            )
        }
    )


# ---------------------------------------------------------------------------
# CONVERTISSEURS
# ---------------------------------------------------------------------------

def convert_pdf(src: Path, dst: Path):
    """Convertit un PDF en Markdown avec Docling."""
    conv = get_docling_converter()
    print(f"    [Docling] {src.name} → {dst.name}")
    result = conv.convert(str(src))
    md = result.document.export_to_markdown()
    dst.write_text(md, encoding="utf-8")


def convert_html(src: Path, dst: Path):
    """Convertit un HTML en Markdown via markdownify."""
    print(f"    [markdownify] {src.name} → {dst.name}")
    html = src.read_text(encoding="utf-8")
    md = mdify(html)
    dst.write_text(md, encoding="utf-8")


# ---------------------------------------------------------------------------
# LOGIQUE PRINCIPALE
# ---------------------------------------------------------------------------

def process_downloads():
    if not DOWNLOADS_DIR.exists():
        print(f"Dossier {DOWNLOADS_DIR} introuvable – rien à convertir.", file=sys.stderr)
        sys.exit(1)

    MARKDOWN_DIR.mkdir(exist_ok=True)

    total = 0
    skipped = 0
    errors = 0

    for category_dir in sorted(DOWNLOADS_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        category = category_dir.name
        md_cat_dir = MARKDOWN_DIR / category
        md_cat_dir.mkdir(exist_ok=True)
        print(f"\n=== {category} ===")

        for src in sorted(category_dir.iterdir()):
            if not src.is_file():
                continue

            ext = src.suffix.lower()
            if ext == ".pdf":
                dst = md_cat_dir / (src.stem + ".md")
            elif ext in (".html", ".htm"):
                dst = md_cat_dir / (src.stem + ".md")
            else:
                continue

            if dst.exists():
                print(f"    → {dst.name} déjà présent, sauté")
                skipped += 1
                continue

            try:
                if ext == ".pdf":
                    convert_pdf(src, dst)
                else:
                    convert_html(src, dst)
                total += 1
            except Exception as exc:
                print(f"    [ERREUR] {src.name} : {exc}")
                errors += 1

            time.sleep(0.2)

    print(f"\nDone. {total} convertis, {skipped} déjà présents, {errors} erreurs.")


if __name__ == "__main__":
    process_downloads()
