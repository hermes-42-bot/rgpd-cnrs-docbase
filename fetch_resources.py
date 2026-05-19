import argparse
import re
import os
import sys
import time
import ssl
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent
BIBTEX_DIR = REPO_ROOT / "bibtex"
DOWNLOADS_DIR = REPO_ROOT / "downloads"
BACKOFF = 1.0
RETRIES = 2

# ---------------------------------------------------------------------------
# UTILITAIRES
# ---------------------------------------------------------------------------

def extract_urls(text):
    """Extrait les URLs contenues dans \\url{...} ou brutes."""
    pattern_url_cmd = r"\\\\url\{(https?://[^}]+)\}"
    urls = re.findall(pattern_url_cmd, text)
    urls += re.findall(r"(https?://[\w\-.:/%?_#=&+~]+)", text)
    return list(dict.fromkeys(urls))


def safe_filename(key, url):
    """Construit un nom de fichier sûr à partir de la clé BibTeX et de l'URL."""
    parsed = urlparse(url)
    base = os.path.basename(parsed.path) or "index"
    if "." in base[-6:]:
        ext = base.split(".")[-1]
        name = f"{key}.{ext}"
    else:
        name = f"{key}.html"
    return name


def fetch(url, dest_path, verify_ssl=True):
    """Télécharge url vers dest_path avec retry. Retourne True si OK."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; RGPD-CNRS-Downloader/1.0; "
            "+https://github.com/hermes-42-bot/rgpd-cnrs-docbase)"
        )
    }
    req = urllib.request.Request(url, headers=headers)

    ctx = None
    if not verify_ssl:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    for attempt in range(1, RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
                data = response.read()
            if len(data) == 0:
                print(f"    [AVERTISSEMENT] Fichier vide ({url})")
                return False
            dest_path.write_bytes(data)
            return True
        except Exception as exc:
            print(f"    [TENTATIVE {attempt}/{RETRIES}] {exc}")
            if attempt < RETRIES:
                time.sleep(BACKOFF * attempt)
    return False


# ---------------------------------------------------------------------------
# LOGIQUE PRINCIPALE
# ---------------------------------------------------------------------------

def list_urls(bib_path):
    """Affiche la liste des URLs contenues dans un .bib, par entrée."""
    raw = bib_path.read_text(encoding="utf-8")
    entries = re.split(r"(?=@\w+\{)", raw)
    for block in entries:
        if not block.strip():
            continue
        key_match = re.search(r"@\w+\{(\S+),", block)
        if not key_match:
            continue
        key = key_match.group(1)
        urls = extract_urls(block)
        if urls:
            for url in urls:
                print(f"{bib_path.stem}\t{key}\t{url}")


def process_bib_file(bib_path, category_dir, verify_ssl=True):
    """Parse un .bib, télécharge les ressources, met à jour les entrées."""
    raw = bib_path.read_text(encoding="utf-8")
    entries = re.split(r"(?=@\w+\{)", raw)
    if not entries:
        return

    updated_blocks = []
    for block in entries:
        if not block.strip():
            updated_blocks.append(block)
            continue

        key_match = re.search(r"@\w+\{(\S+),", block)
        if not key_match:
            updated_blocks.append(block)
            continue
        key = key_match.group(1)
        urls = extract_urls(block)

        if not urls:
            updated_blocks.append(block)
            continue

        print(f"  [{key}] -> {len(urls)} URL(s)")
        for url in urls:
            fname = safe_filename(key, url)
            dest = category_dir / fname
            if dest.exists():
                print(f"    Déjà présent : {fname}")
            else:
                print(f"    Téléchargement : {url} -> {fname}")
                ok = fetch(url, dest, verify_ssl=verify_ssl)
                if ok:
                    print(f"    ✓ OK ({dest.stat().st_size} octets)")
                else:
                    print(f"    ✗ ÉCHEC")
                time.sleep(BACKOFF)

            file_field = f"  file = {{downloads/{category_dir.name}/{fname}}},\n"
            if "file = {" not in block:
                block = block.rstrip()
                if block.endswith(",\n"):
                    block = block[:-2] + "\n"
                elif block.endswith(","):
                    block = block[:-1] + "\n"
                last_brace = block.rfind("}")
                if last_brace != -1:
                    block = block[:last_brace] + file_field + block[last_brace:]

        updated_blocks.append(block)

    new_raw = "".join(updated_blocks)
    bib_path.write_text(new_raw, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Télécharge les ressources référencées dans les .bib du projet RGPD-CNRS."
    )
    parser.add_argument(
        "--no-verify-ssl",
        action="store_true",
        help="Désactiver la vérification des certificats SSL (utile pour certains sites CNRS).",
    )
    parser.add_argument(
        "--urls-only", "-u",
        action="store_true",
        help="Affiche uniquement la liste des URLs (catégorie, clé, URL) sans télécharger.",
    )
    args = parser.parse_args()

    if not BIBTEX_DIR.exists():
        print(f"Dossier {BIBTEX_DIR} introuvable.", file=sys.stderr)
        sys.exit(1)

    if args.urls_only:
        print("# category\tkey\turl")
        for bib_file in sorted(BIBTEX_DIR.glob("*.bib")):
            list_urls(bib_file)
        sys.exit(0)

    DOWNLOADS_DIR.mkdir(exist_ok=True)

    for bib_file in sorted(BIBTEX_DIR.glob("*.bib")):
        category = bib_file.stem
        category_dir = DOWNLOADS_DIR / category
        category_dir.mkdir(exist_ok=True)
        print(f"\n=== {bib_file.name} ===")
        process_bib_file(bib_file, category_dir, verify_ssl=not args.no_verify_ssl)

    print("\nDone.")


if __name__ == "__main__":
    main()
