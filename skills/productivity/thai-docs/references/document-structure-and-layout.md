# Thai document structure and layout

Use the precedence and numeric defaults in SKILL.md. This reference explains how to apply them; it does not define another default profile.

## Structure by deliverable

- **Essay:** use a title followed by connected prose with an introduction, development, and conclusion. These are rhetorical parts, not mandatory visible headings. Choose paragraph count for the argument and requested length. Add section labels only when the assignment asks for them. Include author/student details only when supplied and requested, in the location specified by the assignment.
- **Report:** organize sections around the subject and reader's needs. An empirical report may need objectives, methods, results, discussion, and conclusions; a literature report may need thematic sections and synthesis instead. Use only sections the content supports. Keep heading levels consecutive; if headings are numbered, keep that numbering consistent. Include a cover, contents page, abstract, or appendices when requested or justified by the document's length and purpose. For the user's current preferred report style, use the later preferences in [compact-report-example.md](compact-report-example.md).
- **Official document:** follow the supplied form, field order, identifiers, signature areas, and institution's typography. For government external letters, use [government-correspondence-layout.md](government-correspondence-layout.md); for a `บันทึกข้อความ` (`แบบที่ ๒๙`) internal memo, use that reference and [internal-government-memo-layout.md](internal-government-memo-layout.md) when no conflicting applicable form is supplied. These profiles do not govern every official document. If no form is available for another official-document type, clarify the type and mandatory requirements before claiming compliance. A generic formal report layout is only a draft fallback.

For formatting-only requests, retain the existing text, section order, citations, and meaning. For restructuring requests, map existing material into the new outline before editing so that caveats and necessary sections are not lost.

## Inspect a template or existing document

For DOCX, inspect section sizes and margins, styles plus direct formatting, heading levels, paragraph spacing/indentation, numbering, header/footer distances, and page/section breaks. Look for table widths, repeated header rows, caption placement, and page-number fields. Change the styles actually used by the content; changing Normal alone may leave direct formatting untouched.

For PDF exemplars, inspect page geometry and rendered pages to infer typography, spacing, and alignment. Treat inferred measurements as approximate. Match the recurring body layout as well as the first page; do not claim exact Word style recovery from a PDF.

Distinguish intentional variations, such as a cover or landscape table section, from accidental inconsistencies. Preserve intentional variations.

## Implement consistent formatting

- Use Title for the document title and Heading 1/2/3 for actual section levels, including unnumbered headings. Use automatic numbering only when the selected profile calls for it. Use contents fields when they update reliably, and verify displayed page numbers after final export. A borderless two-column contents layout is suitable when fields cannot reproduce the requested style; confirm every number against the rendered destination page.
- Define body indentation, alignment, and spacing once. Give captions, table cells, references, and metadata their own styles where their layout differs. Do not apply the body's first-line indent to every paragraph indiscriminately.
- Set line spacing inside a paragraph independently from spacing before and after that paragraph. For the current user preference, use 1.0 line spacing while preserving the chosen paragraph gaps.
- Set headings to stay with their following paragraph. Enable widow/orphan control for body text; avoid keeping entire long paragraphs or whole sections together if that creates large gaps.
- Use paragraph and section settings for layout. Avoid manual line breaks at the visual end of each line: Thai text must reflow when fonts or page widths change. Inspect Thai marks and justified spacing in the render; do not insert spaces between Thai words merely to force alignment.
- Fit tables within the available text width. Set predictable column widths and repeat header rows across pages. Keep short rows together; allow a row taller than a page to split or restructure it. Prefer a landscape section or a simpler table to unreadably small text when the template permits.
- Preserve image aspect ratios. Keep each figure with its caption, preferably using inline placement for predictable flow. Keep table captions with their tables and apply one caption placement convention throughout.
- Use actual page-number fields. Preserve intentional numbering restarts and first-page header/footer differences; verify the displayed sequence in the PDF.

## Resolve pagination defects

Inspect the rendered result, because DOCX settings alone cannot show the final line and page breaks.

1. Fix accidental empty paragraphs, manual breaks, excessive spacing, and inappropriate keep-with-next chains first. Check section-break types before removing an apparent blank page.
2. Resolve isolated headings, split captions, clipped table cells, and oversized figures using their local paragraph/table/image settings.
3. For a page limit, tighten the writing when rewriting is authorized and adjust optional layout choices within the agreed profile. Preserve mandatory font sizes and margins. If content must remain unchanged and still cannot fit, explain the conflict and request a choice between length and layout requirements.
4. Re-export after changes and check all pages for new overflow or numbering changes. Use readable page images to inspect Thai glyphs and dense regions; a contact sheet alone is insufficient.

The bundled verifier supplies basic artifact evidence. It does not verify heading hierarchy, actual margins in every section, paragraph spacing, table fit, or visual quality. Inspect those separately and distinguish automated results from visual review.
