#!/usr/bin/env python3
"""Portable, dependency-light verification for a Thai DOCX/PDF pair.

Returns JSON evidence. Required checks fail the process; optional unavailable
checks are reported without pretending they passed.
"""
from __future__ import annotations
import argparse, hashlib, json, re, shutil, subprocess, sys, zipfile
from pathlib import Path


def run(cmd):
    exe = shutil.which(cmd[0])
    if not exe:
        return None, f"missing executable: {cmd[0]}"
    try:
        p = subprocess.run([exe, *cmd[1:]], text=True, capture_output=True, check=False)
        return {"returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}, None
    except OSError as e:
        return None, str(e)


def sha256(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docx", type=Path, required=True)
    ap.add_argument("--pdf", type=Path, required=True)
    ap.add_argument("--render-dir", type=Path)
    ap.add_argument("--required-font")
    ap.add_argument("--forbid-numeric-markers", action="store_true")
    args = ap.parse_args()
    result = {"status": "PASS", "checks": {}, "limitations": [], "errors": []}
    for label, p in (("docx", args.docx), ("pdf", args.pdf)):
        if not p.is_file():
            result["errors"].append(f"missing {label}: {p}")
        else:
            result["checks"][f"{label}_sha256"] = sha256(p)
    if result["errors"]:
        result["status"] = "BLOCKED"
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 2

    # DOCX package/text checks, no absolute paths or external libraries needed.
    with zipfile.ZipFile(args.docx) as z:
        names = set(z.namelist())
        if "[Content_Types].xml" not in names or "word/document.xml" not in names:
            result["errors"].append("invalid DOCX package")
        xml = z.read("word/document.xml").decode("utf-8", "replace")
        all_xml = "\n".join(z.read(n).decode("utf-8", "replace") for n in names if n.endswith(".xml"))
    result["checks"]["docx_package"] = not result["errors"]
    result["checks"]["docx_numeric_markers"] = len(re.findall(r"\[\d+\]", all_xml))
    result["checks"]["docx_has_a4_dimensions"] = ("w:w=\"11906\"" in xml and "w:h=\"16838\"" in xml) or ("11906" in xml and "16838" in xml)
    result["checks"]["docx_has_font_bindings"] = all(x in all_xml for x in ("w:eastAsia", "w:ascii", "w:hAnsi"))
    if not result["checks"]["docx_package"] or result["checks"]["docx_numeric_markers"]:
        result["errors"].append("DOCX package/marker check failed")
    if not result["checks"]["docx_has_font_bindings"]:
        result["limitations"].append("DOCX font bindings are not complete")

    info, err = run(["pdfinfo", str(args.pdf)])
    if err:
        result["limitations"].append(err)
    else:
        assert info is not None
        result["checks"]["pdfinfo_returncode"] = info["returncode"]
        result["checks"]["pdf_pages"] = int(re.search(r"^Pages:\s+(\d+)", info["stdout"], re.M).group(1)) if re.search(r"^Pages:\s+(\d+)", info["stdout"], re.M) else None
        result["checks"]["pdf_a4"] = bool(re.search(r"Page size:\s+595(?:\.\d+)? x 841(?:\.\d+)? pts", info["stdout"]))
        if info["returncode"] or not result["checks"]["pdf_a4"]:
            result["errors"].append("PDF metadata/page geometry check failed")

    text, err = run(["pdftotext", str(args.pdf), "-"])
    if err:
        result["limitations"].append(err)
    else:
        assert text is not None
        pdf_text = text["stdout"]
        result["checks"]["pdf_numeric_markers"] = len(re.findall(r"\[\d+\]", pdf_text))
        result["checks"]["pdf_replacement_chars"] = pdf_text.count("�")
        if result["checks"]["pdf_numeric_markers"] or result["checks"]["pdf_replacement_chars"]:
            result["errors"].append("PDF text marker/replacement-character check failed")

    fonts, err = run(["pdffonts", str(args.pdf)])
    if err:
        result["limitations"].append(err)
    else:
        assert fonts is not None
        result["checks"]["pdf_embedded_fonts"] = bool(re.search(r"\byes\s+yes\b", fonts["stdout"]))
        if args.required_font:
            result["checks"]["required_font_seen"] = args.required_font.lower() in fonts["stdout"].lower()
            if not result["checks"]["required_font_seen"]:
                result["limitations"].append(f"requested font not visibly named by pdffonts: {args.required_font}")

    if args.render_dir:
        args.render_dir.mkdir(parents=True, exist_ok=True)
        render, err = run(["pdftoppm", "-png", "-r", "120", str(args.pdf), str(args.render_dir / "page")])
        if err:
            result["limitations"].append(err)
        else:
            rendered = sorted(args.render_dir.glob("page-*.png"))
            result["checks"]["rendered_pages"] = len(rendered)
            if result["checks"].get("pdf_pages") and len(rendered) != result["checks"]["pdf_pages"]:
                result["errors"].append("rendered page count differs from PDF page count")

    if result["errors"]:
        result["status"] = "BLOCKED"
    elif result["limitations"]:
        result["status"] = "PASS WITH LIMITATIONS"
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] != "BLOCKED" else 2

if __name__ == "__main__":
    raise SystemExit(main())
