# Decision specification

Use UTF-8 JSON. Prefer the compact authoring shape; the legacy verbose shape remains accepted. Both normalize to the same page model.

## Compact shape

```json
{
  "i": "draft-id",
  "l": "en",
  "t": "Choose the direction",
  "c": "What happens after this review.",
  "q": [{
    "i": "layout", "p": "Which layout?", "w": "This changes navigation.",
    "t": "s", "r": true, "a": true,
    "o": [
      ["focused", "Focused page", "One route with anchored sections.", "Fastest stable fit."],
      ["multi", "Multiple pages", "Clear separation with more navigation work."]
    ]
  }]
}
```

Root keys: `i` ID, `l` locale (`en` or `th`, default `en`), `t` title, `c` context, and `q` questions.

Question keys:

- `i`, `p`, `w`: unique ID, prompt, and consequence.
- `t`: `s` single, `m` multi, or `x` text.
- `r`: required boolean; `a`: allow-other boolean.
- `n` / `m`: minimum/maximum count for multi-choice.
- `o`: option tuples `[id, label, details]`. A fourth string marks that option recommended and gives its reason. Use at most one.
- `if`: optional visibility expression.

## Conditional branches

- `['question-id', 'option-id']`: show when that earlier choice is selected.
- `['all', condition, condition]`: require every child.
- `['any', condition, condition]`: require at least one child.
- `['not', condition]`: invert one child.

Reference only an earlier single- or multi-choice question and one of its option IDs. This ordering prevents cycles. A branch whose dependency is itself hidden remains hidden. Hidden answers stay in browser autosave but are excluded from validation, progress, review, recommendations, copied briefs, and saved responses.

## Legacy verbose fields

The existing `id`, `locale`, `title`, `context`, and `questions` root fields remain valid. Questions may use `id`, `prompt`, `why`, `type`, `required`, `allow_other`, `min`, `max`, `options`, and `when`. Options may use `id`, `label`, `details`, `recommended`, and `recommendation_reason`. Use the same condition arrays for `when`.

Unknown verbose fields are ignored. Choice questions require at least two uniquely identified options. Recommended options require a reason. Multi-choice bounds must be non-negative, ordered, and no larger than the option count.

## Saved response

The response keeps `boxing-me-response-v1`, `spec_id`, `spec_title`, `saved_at`, `answers`, and `overall_notes`. Each active answer includes its question, selected IDs and labels, written/other input, notes, and `source` (`agent` or `user`). `custom_questions` stores definitions created through **Add question**. Inactive questions are omitted.

## Writing checks

- Cover material edge cases, dependencies, failure states, and costly-to-reverse choices.
- Keep labels short; put behavior, cost, risk, and tradeoffs in details.
- Avoid duplicate or leading choices outside the explicit recommendation.
- Omit a recommendation when evidence is insufficient or preference is subjective.
- Never request passwords, keys, tokens, or similarly sensitive input.
