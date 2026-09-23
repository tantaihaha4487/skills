#!/usr/bin/env python3
"""Check a Thai DOCX and, when available, its rendered PDF. Emit JSON evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str]) -> tuple[subprocess.CompletedProcess[str] | None, str | None]:
    executable = shutil.which(command[0])
    if not executable:
        return None, f"missing executable: {command[0]}"
    try:
        return subprocess.run([executable, *command[1:]], text=True, capture_output=True, check=False), None
    except OSError as error:
        return None, str(error)


def normalized_font(name: str) -> str:
    return re.sub(r"[\s_-]+", "", re.sub(r"^[A-Z]{6}\+", "", name)).lower()


def check_docx(path: Path, required_font: str | None, forbid_markers: bool, checks: dict, errors: list[str]) -> None:
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if archive.testzip() is not None or "[Content_Types].xml" not in names or "word/document.xml" not in names:
                raise ValueError("incomplete or damaged DOCX package")
            document = ET.fromstring(archive.read("word/document.xml"))
            word_parts = [ET.fromstring(archive.read(name)) for name in names
                          if name.startswith("word/") and name.endswith(".xml")]
    except (OSError, zipfile.BadZipFile, ET.ParseError, ValueError, KeyError) as error:
        checks["docx_package"] = False
        errors.append(f"DOCX package check failed: {error}")
        return

    checks["docx_package"] = True
    page_sizes = [(int(node.get(W + "w", "0")), int(node.get(W + "h", "0")))
                  for node in document.iter(W + "pgSz")]
    checks["docx_has_a4_dimensions"] = bool(page_sizes) and all(
        abs(width - 11906) <= 1 and abs(height - 16838) <= 1 for width, height in page_sizes
    )
    if not checks["docx_has_a4_dimensions"]:
        errors.append("DOCX page geometry is not A4 portrait in every section")

    all_text = " ".join(node.text or "" for root in word_parts for node in root.iter(W + "t"))
    checks["docx_numeric_markers"] = len(re.findall(r"\[\d+\]", all_text))
    if forbid_markers and checks["docx_numeric_markers"]:
        errors.append("numeric citation markers remain in DOCX")

    font_nodes = [node for root in word_parts for node in root.iter(W + "rFonts")]
    slots = ("ascii", "hAnsi", "eastAsia", "cs")
    checks["docx_has_font_bindings"] = bool(font_nodes) and all(
        all(node.get(W + slot) for slot in slots) for node in font_nodes
    )
    if not checks["docx_has_font_bindings"]:
        errors.append("DOCX contains incomplete four-slot font bindings")
    if required_font:
        expected = normalized_font(required_font)
        checks["docx_required_font_only"] = bool(font_nodes) and all(
            normalized_font(node.get(W + slot, "")) == expected
            for node in font_nodes for slot in slots
        )
        if not checks["docx_required_font_only"]:
            errors.append(f"DOCX contains font bindings outside {required_font}")


def check_pdf(path: Path, required_font: str | None, forbid_markers: bool,
              render_dir: Path | None, checks: dict, errors: list[str]) -> None:
    info, issue = run(["pdfinfo", str(path)])
    if issue or info is None or info.returncode:
        errors.append(f"PDF metadata check failed: {issue or (info.stderr.strip() if info else '')}")
        return
    page_match = re.search(r"^Pages:\s+(\d+)", info.stdout, re.M)
    checks["pdf_pages"] = int(page_match.group(1)) if page_match else None
    page_info, page_issue = run(["pdfinfo", "-f", "1", "-l", str(checks["pdf_pages"] or 1), str(path)])
    page_sizes = re.findall(r"^Page\s+\d+ size:\s+([\d.]+) x ([\d.]+) pts", page_info.stdout if page_info else "", re.M)
    checks["pdf_a4"] = bool(checks["pdf_pages"]) and not page_issue and page_info is not None and page_info.returncode == 0 and len(page_sizes) == checks["pdf_pages"] and all(
        abs(float(width) - 595.28) < 1 and abs(float(height) - 841.89) < 1
        for width, height in page_sizes
    )
    if not checks["pdf_a4"]:
        errors.append("PDF page count or A4 portrait geometry check failed")

    text, issue = run(["pdftotext", str(path), "-"])
    if issue or text is None or text.returncode:
        errors.append(f"PDF text extraction failed: {issue or (text.stderr.strip() if text else '')}")
    else:
        checks["pdf_numeric_markers"] = len(re.findall(r"\[\d+\]", text.stdout))
        checks["pdf_replacement_chars"] = text.stdout.count("�")
        if forbid_markers and checks["pdf_numeric_markers"]:
            errors.append("numeric citation markers remain in PDF")
        if checks["pdf_replacement_chars"]:
            errors.append("PDF contains replacement characters")

    fonts, issue = run(["pdffonts", str(path)])
    if issue or fonts is None or fonts.returncode:
        errors.append(f"PDF font inspection failed: {issue or (fonts.stderr.strip() if fonts else '')}")
    else:
        rows = [line.split() for line in fonts.stdout.splitlines()[2:] if line.strip()]
        checks["pdf_font_names"] = [row[0] for row in rows]
        checks["pdf_embedded_fonts"] = bool(rows) and all(len(row) >= 5 and row[3].lower() == "yes" for row in rows)
        if not checks["pdf_embedded_fonts"]:
            errors.append("PDF has unembedded or uninspectable fonts")
        if required_font:
            expected = normalized_font(required_font)
            checks["required_font_only"] = bool(rows) and all(normalized_font(row[0]).startswith(expected) for row in rows)
            if not checks["required_font_only"]:
                errors.append(f"PDF contains a font outside {required_font}")

    if render_dir:
        render_dir.mkdir(parents=True, exist_ok=True)
        fresh_dir = Path(tempfile.mkdtemp(prefix="run-", dir=render_dir))
        render, issue = run(["pdftoppm", "-png", "-r", "120", str(path), str(fresh_dir / "page")])
        if issue or render is None or render.returncode:
            errors.append(f"PDF rendering failed: {issue or (render.stderr.strip() if render else '')}")
        else:
            pages = sorted(fresh_dir.glob("page-*.png"))
            checks["render_output_dir"] = str(fresh_dir)
            checks["rendered_pages"] = len(pages)
            if not pages or len(pages) != checks.get("pdf_pages"):
                errors.append("rendered page count differs from PDF page count")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docx", type=Path, required=True)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--render-dir", type=Path)
    parser.add_argument("--required-font")
    parser.add_argument("--forbid-numeric-markers", action="store_true")
    args = parser.parse_args()
    checks: dict = {}
    limitations: list[str] = []
    errors: list[str] = []
    if not args.docx.is_file():
        errors.append(f"missing DOCX: {args.docx}")
    else:
        checks["docx_sha256"] = sha256(args.docx)
        check_docx(args.docx, args.required_font, args.forbid_numeric_markers, checks, errors)
    if args.pdf:
        if not args.pdf.is_file():
            errors.append(f"missing PDF: {args.pdf}")
        else:
            checks["pdf_sha256"] = sha256(args.pdf)
            check_pdf(args.pdf, args.required_font, args.forbid_numeric_markers, args.render_dir, checks, errors)
    else:
        limitations.append("DOCX-only check: pagination, embedded PDF fonts, and visual layout were not verified")
        if args.render_dir:
            errors.append("--render-dir requires --pdf")
    status = "BLOCKED" if errors else ("PASS WITH LIMITATIONS" if limitations else "PASS")
    print(json.dumps({"status": status, "checks": checks, "limitations": limitations, "errors": errors}, ensure_ascii=False, indent=2))
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
