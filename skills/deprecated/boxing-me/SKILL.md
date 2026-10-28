---
name: boxing-me
description: Turn a complex clarification interview into one interactive HTML decision page with recommendations, conditional branches, custom questions, review, and saved responses. Use when the user says "grill me," requests a questionnaire or visual decision brief, wants exhaustive edge-case review, or when three or more material choices block the work.
---

# Box My Decisions

Resolve one decision tree per page; spend agent tokens on the brief, not HTML.

## Workflow

1. Inspect task, codebase, artifacts; answer discoverable questions yourself.
2. Map decisions and dependencies. When relevant, probe scope boundaries, empty/error states, reversibility, compatibility, accessibility, security, and rollout; do not manufacture irrelevant questions.
3. Draft compact JSON from [the decision schema](references/decision-schema.md). Keep full user-facing detail in prompts, consequences, option tradeoffs, and recommendation reasons.
4. For every applicable question:
   - provide distinct choices and a recommended answer when evidence supports one;
   - explain why the decision matters and why the recommendation fits;
   - use a conditional branch when questions apply only after an earlier choice;
   - allow another answer or written input when fixed choices are incomplete.
5. Validate, build, serve:

   ```bash
   python3 <skill-dir>/scripts/decision_page.py validate <spec.json>
   python3 <skill-dir>/scripts/decision_page.py build <spec.json> --output <decision-page.html>
   python3 <skill-dir>/scripts/decision_page.py serve <spec.json> \
     --output <decision-page.html> --response <response.json>
   ```

6. Give the `BOXING_ME_URL` as a clickable link, name the response path, and ask the user to save and confirm. Keep the server running.
7. Read response, including custom questions. Respect settled answers and omit inactive branches. Ask again only when an answer exposes a genuinely new material decision or a missing required active answer.
8. Summarize shared direction and continue the original task. Treat recommendations as suggestions, never consent.

## Page rules

- Prefer 3-7 visible grouped questions; encode dependent questions instead of showing irrelevant branches.
- Use `single` for one choice, `multi` for compatible choices, `text` only for irreducible input.
- Do not preselect recommendations. Let the user choose or apply them explicitly.
- Make required, selected, recommended, invalid, and hidden state understandable without color alone.
- Preserve browser autosave, review, notes, copy, download, server save, and full custom-question builder.
- Use local `Noto Sans` with `Noto Sans Thai` fallback. Keep ordinary copy at weight 200 and emphasis visibly heavier.
- Bind to `127.0.0.1` unless network sharing is requested. Never put secrets in a page.
- Change the spec ID when revisions make saved answers stale.

## Failure handling

- If serving fails, provide validated built HTML (copy/download still works) and report response collection incomplete.
- If response file is missing, ask user to save again or paste copied brief.
- Preserve hidden-branch drafts locally but never treat them as active approval.
- If new evidence invalidates a choice, explain it and reopen only the affected branch.

Report only performed checks. For server-backed presentations, confirm validation, generation, script syntax, no external assets, and a parseable server-saved response.
