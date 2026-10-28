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
    return re.sub(r"^[A-Z]{6}\+|[\s_-]+", "", name).lower()


SEPARATORS = {W + name for name in
              "br commentReference continuationSeparator cr delInstrText "
              "delText endnoteReference fldChar footnoteReference "
              "instrText lastRenderedPageBreak noBreakHyphen ptab separator "
              "softHyphen sym tab".split()}
BOUNDARIES = {W + name for name in
              "altChunk customXml drawing fldSimple hyperlink object pict smartTag sdt subDoc".split()}
SKIP = {W + name for name in "drawing object pict".split()}
STRUCTURE = {W + name for name in "p pPr rPr".split()}


def text_segments(node: ET.Element) -> list[str]:
    """Collect displayed runs without joining across inline Word boundaries."""
    segments: list[str] = []
    current = []

    def flush() -> None:
        if current:
            segments.append("".join(current))
            current.clear()

    def visit(child: ET.Element) -> None:
        tag = child.tag
        if tag == W + "t":
            current.append(child.text or "")
        elif tag in SEPARATORS:
            flush()
        elif tag in BOUNDARIES:
            flush()
            if tag not in SKIP:
                segments.extend(text_segments(child))
            flush()
        elif tag in STRUCTURE:
            return
        else:
            for nested in child:
                visit(nested)

    for child in node:
        visit(child)
    flush()
    return segments


def is_a4(width: float, height: float, allow_landscape: bool,
          portrait_width: float, portrait_height: float) -> bool:
    portrait = abs(width - portrait_width) <= 1 and abs(height - portrait_height) <= 1
    landscape = abs(width - portrait_height) <= 1 and abs(height - portrait_width) <= 1
    return portrait or (allow_landscape and landscape)


def check_docx(path: Path, required_font: str | None, forbid_markers: bool,
               allow_landscape: bool, checks: dict, errors: list[str]) -> None:
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if archive.testzip() is not None or "[Content_Types].xml" not in names or "word/document.xml" not in names:
                raise ValueError("incomplete or damaged DOCX package")
            document = ET.fromstring(archive.read("word/document.xml"))
            word_parts = [document if name == "word/document.xml" else ET.fromstring(archive.read(name))
                          for name in names if name.startswith("word/") and name.endswith(".xml")]
    except (OSError, zipfile.BadZipFile, ET.ParseError, ValueError, KeyError) as error:
        checks["docx_package"] = False
        errors.append(f"DOCX package check failed: {error}")
        return

    checks["docx_package"] = True
    try:
        page_sizes = [(int(node.get(W + "w", "0")), int(node.get(W + "h", "0")))
                      for node in document.iter(W + "pgSz")]
    except ValueError:
        page_sizes = []
    checks["docx_has_a4_dimensions"] = bool(page_sizes) and all(
        is_a4(width, height, allow_landscape, 11906, 16838) for width, height in page_sizes
    )
    if not checks["docx_has_a4_dimensions"]:
        expected = "A4" if allow_landscape else "A4 portrait"
        errors.append(f"DOCX page geometry is not {expected} in every section")

    checks["docx_numeric_markers"] = sum(
        len(re.findall(r"\[\d+\]", segment))
        for root in word_parts for paragraph in root.iter(W + "p") for segment in text_segments(paragraph))
    if forbid_markers and checks["docx_numeric_markers"]:
        errors.append("numeric citation markers remain in DOCX")

    font_nodes = [node for root in word_parts for node in root.iter(W + "rFonts")]
    slots = ("ascii", "hAnsi", "eastAsia", "cs")
    checks["docx_has_font_bindings"] = bool(font_nodes) and all(
        all(node.get(W + slot) for slot in slots) for node in font_nodes
    )
    if not checks["docx_has_font_bindings"]:
        errors.append("DOCX contains incomplete four-slot font bindings")
    theme_slots = ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "csTheme", "cstheme")
    checks["docx_has_no_theme_font_bindings"] = not any(
        node.get(W + slot) for node in font_nodes for slot in theme_slots
    )
    if not checks["docx_has_no_theme_font_bindings"]:
        errors.append("DOCX contains competing theme font bindings")
    declared_families = {
        normalized_font(node.get(W + slot, ""))
        for node in font_nodes for slot in slots if node.get(W + slot)
    }
    checks["docx_font_families"] = sorted(declared_families)
    checks["docx_single_font_family"] = bool(declared_families) and len(declared_families) == 1
    if not checks["docx_single_font_family"]:
        errors.append("DOCX declares multiple font families")
    if required_font:
        expected = normalized_font(required_font)
        checks["docx_required_font_only"] = bool(font_nodes) and all(
            normalized_font(node.get(W + slot, "")) == expected
            for node in font_nodes for slot in slots
        )
        if not checks["docx_required_font_only"]:
            errors.append(f"DOCX contains font bindings outside {required_font}")


def check_pdf(path: Path, required_font: str | None, forbid_markers: bool,
              render_dir: Path | None, allow_landscape: bool,
              checks: dict, errors: list[str]) -> None:
    # Ask pdfinfo for the full page range so the document metadata and every
    # page size usually come back in one process. Fall back to the portable
    # two-query path if this Poppler build rejects a large page bound or omits
    # any per-page size records.
    info, issue = run(["pdfinfo", "-f", "1", "-l", "2147483647", str(path)])
    if issue or info is None or info.returncode:
        info, issue = run(["pdfinfo", str(path)])
    if issue or info is None or info.returncode:
        errors.append(f"PDF metadata check failed: {issue or (info.stderr.strip() if info else '')}")
        return
    page_match = re.search(r"^Pages:\s+(\d+)", info.stdout, re.M)
    if not page_match:
        info, issue = run(["pdfinfo", str(path)])
        if issue or info is None or info.returncode:
            errors.append(f"PDF metadata check failed: {issue or (info.stderr.strip() if info else '')}")
            return
        page_match = re.search(r"^Pages:\s+(\d+)", info.stdout, re.M)
    checks["pdf_pages"] = page_match and int(page_match.group(1))
    page_sizes = re.findall(r"^Page\s+\d+ size:\s+([\d.]+) x ([\d.]+) pts", info.stdout, re.M)
    page_info, page_issue = info, None
    if checks["pdf_pages"] and len(page_sizes) != checks["pdf_pages"]:
        page_info, page_issue = run(["pdfinfo", "-f", "1", "-l", str(checks["pdf_pages"]), str(path)])
        page_sizes = re.findall(r"^Page\s+\d+ size:\s+([\d.]+) x ([\d.]+) pts", page_info.stdout if page_info else "", re.M)
    checks["pdf_a4"] = bool(checks["pdf_pages"]) and not page_issue and page_info is not None and page_info.returncode == 0 and len(page_sizes) == checks["pdf_pages"] and all(
        is_a4(float(width), float(height), allow_landscape, 595.28, 841.89)
        for width, height in page_sizes
    )
    if not checks["pdf_a4"]:
        expected = "A4" if allow_landscape else "A4 portrait"
        errors.append(f"PDF page count or {expected} geometry check failed")

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
    parser.add_argument("--allow-landscape", action="store_true")
    args = parser.parse_args()
    checks: dict = {"visual_review": "UNVERIFIED"}
    limitations: list[str] = []
    errors: list[str] = []
    if not args.docx.is_file():
        errors.append(f"missing DOCX: {args.docx}")
    else:
        checks["docx_sha256"] = sha256(args.docx)
        check_docx(args.docx, args.required_font, args.forbid_numeric_markers,
                   args.allow_landscape, checks, errors)
    if args.pdf:
        if not args.pdf.is_file():
            errors.append(f"missing PDF: {args.pdf}")
        else:
            checks["pdf_sha256"] = sha256(args.pdf)
            check_pdf(args.pdf, args.required_font, args.forbid_numeric_markers,
                      args.render_dir, args.allow_landscape, checks, errors)
    else:
        limitations.append("DOCX-only check: pagination, embedded PDF fonts, and visual layout were not verified")
        if args.render_dir:
            errors.append("--render-dir requires --pdf")
    if checks["visual_review"] == "UNVERIFIED":
        limitations.append("Human visual review is unverified")
    status = "BLOCKED" if errors else ("PASS WITH LIMITATIONS" if limitations else "PASS")
    print(json.dumps({"status": status, "checks": checks, "limitations": limitations, "errors": errors}, ensure_ascii=False, indent=2))
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
