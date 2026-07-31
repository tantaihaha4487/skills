---
name: boxing-me
description: Consolidate a large or repetitive set of clarification questions into one polished, interactive HTML decision page with checkboxes, radio choices, recommendations, explanations, free-form feedback, review, and a saved response for the agent to consume. Use when a user says "grill me", asks for a questionnaire or decision brief, wants to review a draft visually, is frustrated by many back-and-forth questions, or when three or more material choices would otherwise block or significantly change the work.
---

# Box My Decisions

Replace a long question-by-question interview with one decision page. Ask only decisions that materially change scope, behavior, cost, risk, or presentation; continue independently on everything else.

## Workflow

1. Inspect the task and available artifacts before asking anything. Resolve discoverable facts yourself.
2. Draft a JSON specification following [the decision schema](references/decision-schema.md). Group related choices, use plain language, and keep the page short enough to scan.
3. For each question:
   - explain why the decision matters;
   - provide concrete, mutually distinct choices;
   - mark exactly one recommendation when a sensible default exists;
   - explain the recommendation and each option's meaningful tradeoff;
   - include `other` or a free-text question when fixed choices cannot cover legitimate answers.
4. Generate and serve the page:

   ```bash
   python3 <skill-dir>/scripts/decision_page.py serve <spec.json> \
     --output <decision-page.html> \
     --response <response.json>
   ```

5. Read the printed `BOXING_ME_URL`, give it to the user as a clickable link, identify the response path, and ask them to click **Save decisions** and tell you when done. Keep the server process running.
6. After the user confirms, read the response JSON. Respect `selected`, `other`, and `notes`; do not reopen settled choices. If required answers are absent, ask only for those missing answers.
7. Summarize the chosen direction and continue the original task. Treat recommendations as suggestions, never as consent.

## Page design rules

- Prefer 3-7 grouped questions. Split only when the decisions truly cannot fit coherently.
- Use `single` for one-of-many, `multi` only when choices may coexist, and `text` for irreducible open input.
- Do not preselect recommendations. The user must actively choose, or use **Apply recommendations**.
- Make required state, selection state, recommendation, rationale, and validation visible without relying on color alone.
- Include a final review, overall notes, autosave in the browser, copy, JSON download, and server save.
- Use `Noto Sans` with `Noto Sans Thai` fallback as the default local-first font stack; do not add a network font dependency.
- Bind the server to `127.0.0.1` unless the user explicitly requests network sharing. Never place secrets in the page.
- Use a new response filename for a materially revised draft so stale answers cannot be mistaken for current approval.

## Decision threshold

Do not invoke the page for one or two simple questions. Use it when there are at least three material decisions, the user explicitly asks for this workflow, or a visual review will substantially reduce ambiguity. If a safe default permits progress, state the assumption and proceed rather than manufacturing a question.

## Failure handling

- If the server cannot start, run the `build` command and provide the HTML file link. The user can copy the agent brief or download JSON.
- If the user closes or refreshes the page, restore answers from browser autosave.
- If the response file is missing after confirmation, ask the user to reopen the same URL and click **Save decisions**, or paste the copied agent brief.
- If a choice becomes invalid after new evidence, explain the evidence and request review only for the affected decision.

## Verification

Before presenting the page, run:

```bash
python3 <skill-dir>/scripts/decision_page.py validate <spec.json>
python3 <skill-dir>/scripts/decision_page.py build <spec.json> --output <decision-page.html>
```

Confirm that generation succeeds, no external assets are required, and the served save endpoint writes parseable JSON. Report only checks actually performed.
