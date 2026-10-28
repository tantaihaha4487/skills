from __future__ import annotations

import re

_PLACEHOLDER_PATTERN = re.compile(r"\$\{[^}]+}|@[A-Za-z0-9_.-]+@")


def _strip_yaml_comment(value: str) -> str:
    quote: str | None = value[0] if value[:1] in {"'", '"'} else None
    escaped = False
    index = 1 if quote else 0
    while index < len(value):
        character = value[index]
        if quote == '"':
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quote = None
        elif quote == "'":
            if character == "'":
                if index + 1 < len(value) and value[index + 1] == "'":
                    index += 1
                else:
                    quote = None
        elif character == "#" and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
        index += 1
    return value.rstrip()


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def has_unresolved_placeholders(values: dict[str, str]) -> bool:
    return any(_PLACEHOLDER_PATTERN.search(value) for value in values.values())


def top_level_yaml(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if not line or line[0].isspace() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$", line)
        if match:
            value = _strip_yaml_comment(match.group(2).strip())
            values[match.group(1)] = _unquote(value)
    return values
