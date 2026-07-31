# Decision specification

Use UTF-8 JSON. Unknown fields are ignored so specifications remain forward-compatible.

## Shape

```json
{
  "id": "unique-draft-id",
  "locale": "en",
  "title": "Choose the direction",
  "context": "A short description of what the agent will do after this review.",
  "questions": [
    {
      "id": "layout",
      "prompt": "Which layout should we use?",
      "why": "This changes navigation and implementation effort.",
      "type": "single",
      "required": true,
      "options": [
        {
          "id": "focused",
          "label": "Focused single page",
          "details": "One continuous page with anchored sections.",
          "recommended": true,
          "recommendation_reason": "It is the fastest stable fit for the current amount of content."
        },
        {
          "id": "multi",
          "label": "Multiple pages",
          "details": "Separate routes for each major topic. Better separation, more navigation work."
        }
      ],
      "allow_other": true
    }
  ]
}
```

## Fields

- Root `id`: stable identifier for this draft. Change it when revised questions invalidate old answers.
- Root `locale`: optional built-in interface language, `en` or `th`; defaults to `en`.
- Root `title`: short action-oriented heading.
- Root `context`: what is being decided and what happens next.
- `questions`: one or more question objects with unique IDs.
- Question `prompt`: direct question.
- Question `why`: concise consequence of the decision.
- Question `type`: `single`, `multi`, or `text`.
- Question `required`: boolean, default `false`.
- Question `options`: required for `single` and `multi`; use at least two options with unique IDs.
- Question `allow_other`: add a free-text alternative to a choice question.
- Question `min` / `max`: optional selected-count bounds for `multi`.
- Option `label`: concise choice name.
- Option `details`: behavior, cost, and tradeoffs; do not repeat the label.
- Option `recommended`: boolean. Use at most one per question.
- Option `recommendation_reason`: required on a recommended option; explain why it fits this task.

The page always adds overall notes and an answer review. A saved response records the spec ID, timestamp, selected option IDs and labels, other text, per-question notes, and overall notes.

## Writing checks

- Avoid duplicate choices disguised by wording.
- Avoid leading language outside the explicitly labeled recommendation.
- Do not use a recommendation when evidence is insufficient or preference is entirely subjective.
- Say when a choice is reversible or expensive to change later.
- Put technical detail in `details`; keep `label` and `prompt` accessible.
- Never request passwords, API keys, private tokens, or similarly sensitive input.
