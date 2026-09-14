# Numeric citation-marker removal and verification

Use this reference when a user asks to remove bracketed numeric citations such as `[2][14]` from an existing Thai DOCX/report.

## Scope decision

- Treat `\[\d+\]` as a numeric citation marker, not as an ordinary number.
- If the user says “remove all” or gives an example such as `.[2][14]`, remove every bracketed numeric marker from the report body **and** the numeric labels before bibliography entries.
- Preserve normal scientific numbers: dates, years, measurements, percentages, quantities, section numbers, chemical notation, and ranges such as `24 มีนาคม 1989`, `258,000 บาร์เรล`, `14–70%`, and `2011–2012`.
- Remove only the bracketed marker; preserve the sentence punctuation before it. For example, `ประโยค.[2][14]` becomes `ประโยค.`.
- If the user asks to remove markers only from the body, leave bibliography numbering untouched and state that scope explicitly. Do not silently choose a mixed citation state.

## Reproducible procedure

1. Work from a copy of the existing DOCX and its verified source-of-truth. Do not overwrite the only original.
2. Apply the exact transformation to the editable source with `re.sub(r'\[\d+\]', '', text)` or an equivalent targeted operation. Count markers before and after; assert the post-count is zero when “all” was requested.
3. Rebuild the DOCX and its PDF companion using the same Thai font/layout generator. Do not remove unrelated content or scientific numbers while changing citations.
4. Validate the actual DOCX and PDF, not only the source text:
   - run the DOCX package validator;
   - extract DOCX/PDF text and assert `re.search(r'\[\d+\]', text)` returns no match;
   - assert required dates, measurements, and result ranges remain;
   - check that bibliography entries and URLs are still present and readable.
5. Re-render every page after the edit. Inspect the first page, a dense table page, the changed citation-heavy page, and the final references page for orphaned punctuation, abnormal spacing, broken wrapping, blank pages, or clipped tables.
6. Report clearly that in-text citation markers were removed. Do not claim the output retains numbered traceability after the markers are gone.

## Metadata and artifact integrity

When rebuilding from a default/template document, explicitly set DOCX core `created` and `modified` to the actual save time instead of inheriting a stale template date. Verify the final metadata and PDF page geometry after the citation edit. Keep the original file hash/path available so the user can distinguish the preserved source from the derived output.

## Do not

- Do not delete every digit in the report; that would destroy dates, measurements, years, section numbering, and scientific results.
- Do not leave a mixture of some `[n]` markers and some removed markers when the request says all.
- Do not invent replacement author-date citations or bibliography metadata merely because numeric markers were removed.
- Do not report success from a Markdown/source count alone; verify the generated DOCX and PDF text plus rendered pages.
