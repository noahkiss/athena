#!/usr/bin/env python3
"""Synthetic note generator for stress/soak tests.

Generates markdown notes sized within a target KB range using category templates.
"""

from __future__ import annotations

import argparse
import json
import random
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable


CATEGORIES = ["home", "journal", "people", "projects", "reading", "tech", "wellness"]

COMMON_WORDS = [
    "agenda",
    "context",
    "note",
    "summary",
    "next",
    "update",
    "review",
    "plan",
    "issue",
    "idea",
    "progress",
    "decision",
    "owner",
    "deadline",
    "impact",
    "status",
    "risk",
]

CATEGORY_WORDS: dict[str, list[str]] = {
    "home": ["kitchen", "garden", "repairs", "utilities", "budget", "cleaning"],
    "journal": ["mood", "reflection", "day", "gratitude", "lesson", "moment"],
    "people": ["call", "meeting", "follow-up", "contact", "relationship", "intro"],
    "projects": ["milestone", "deliverable", "scope", "dependency", "timeline", "backlog"],
    "reading": ["chapter", "excerpt", "thesis", "author", "citation", "summary"],
    "tech": ["service", "latency", "api", "database", "deployment", "monitoring"],
    "wellness": ["sleep", "routine", "nutrition", "exercise", "habit", "recovery"],
}

TAGS: dict[str, list[str]] = {
    "home": ["#home", "#maintenance", "#family"],
    "journal": ["#journal", "#daily", "#reflection"],
    "people": ["#people", "#network", "#followup"],
    "projects": ["#projects", "#planning", "#execution"],
    "reading": ["#reading", "#notes", "#summary"],
    "tech": ["#tech", "#infra", "#observability"],
    "wellness": ["#wellness", "#health", "#habits"],
}

LINK_HOSTS = ["example.com", "notes.local", "internal.test"]


@dataclass
class NoteSpec:
    index: int
    category: str
    size_kb: int
    ambiguous: bool
    filename: str


class TemplateError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic markdown notes for stress tests.")
    parser.add_argument("--count", type=int, default=1000, help="Number of notes to generate.")
    parser.add_argument("--out-dir", type=Path, default=Path("gardener/tests/fixtures/generated"))
    parser.add_argument("--templates-dir", type=Path, default=Path("gardener/tests/fixtures/templates"))
    parser.add_argument("--min-kb", type=int, default=1, help="Minimum note size in KB.")
    parser.add_argument("--max-kb", type=int, default=100, help="Maximum note size in KB.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    parser.add_argument(
        "--ambiguous-rate",
        type=float,
        default=0.2,
        help="Fraction of notes that mix in a secondary category.",
    )
    parser.add_argument(
        "--categories",
        type=str,
        default=None,
        help="Comma-separated list of categories to use (default: all).",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Optional JSON manifest output path.",
    )
    return parser.parse_args()


def load_templates(templates_dir: Path) -> dict[str, str]:
    if not templates_dir.exists():
        raise TemplateError(f"Templates directory not found: {templates_dir}")
    templates: dict[str, str] = {}
    for path in templates_dir.glob("*.md"):
        templates[path.stem] = path.read_text(encoding="utf-8")
    missing = [category for category in CATEGORIES if category not in templates]
    if missing:
        raise TemplateError(f"Missing templates for categories: {', '.join(missing)}")
    return templates


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "note"


def random_date(rng: random.Random) -> str:
    days_ago = rng.randint(0, 365)
    date = datetime.utcnow() - timedelta(days=days_ago, hours=rng.randint(0, 23))
    return date.strftime("%Y-%m-%d")


def choose_tags(category: str, rng: random.Random) -> str:
    tags = rng.sample(TAGS[category], k=2)
    if rng.random() < 0.2:
        tags.append(rng.choice(["#priority", "#idea", "#draft"]))
    return " ".join(tags)


def random_sentence(words: Iterable[str], rng: random.Random, length: int) -> str:
    tokens = [rng.choice(list(words)) for _ in range(length)]
    tokens[0] = tokens[0].capitalize()
    return " ".join(tokens) + "."


def random_paragraph(words: Iterable[str], rng: random.Random, sentences: int = 4) -> str:
    return " ".join(random_sentence(words, rng, rng.randint(6, 12)) for _ in range(sentences))


def build_bullets(words: Iterable[str], rng: random.Random, count: int = 4) -> str:
    lines = []
    for _ in range(count):
        lines.append(f"- {random_sentence(words, rng, rng.randint(5, 9))}")
    return "\n".join(lines)


def build_links(category: str, rng: random.Random, count: int = 3) -> str:
    lines = []
    for idx in range(count):
        host = rng.choice(LINK_HOSTS)
        slug = slugify(f"{category} {idx} reference")
        lines.append(f"- [{category} reference {idx + 1}](https://{host}/{slug})")
    return "\n".join(lines)


def build_code_block(category: str, rng: random.Random) -> str:
    if rng.random() > 0.3:
        return ""
    code = ["```", f"# {category} automation snippet", "status = 'ok'", "print(status)", "```"]
    return "\n".join(code)


def build_edge_case_block(rng: random.Random) -> str:
    if rng.random() > 0.15:
        return ""
    special = "Special chars: <>&\"'[]{}()!@#$%^&*"
    long_line = "Long line: " + ("x" * 5000)
    unicode_line = "Unicode: " + " ".join(["\u2603", "\u03c0", "\u00e9"])
    return "\n".join(["## Edge Cases", special, long_line, unicode_line])


def build_mixed_section(primary: str, secondary: str, rng: random.Random) -> str:
    if primary == secondary:
        return ""
    words = CATEGORY_WORDS[secondary] + COMMON_WORDS
    return "\n".join(
        [
            "## Cross Notes",
            random_paragraph(words, rng, sentences=2),
        ]
    )


def build_title(category: str, rng: random.Random) -> str:
    focus = rng.choice(CATEGORY_WORDS[category])
    return f"{category.title()} update: {focus}"


def note_body(category: str, rng: random.Random) -> str:
    words = CATEGORY_WORDS[category] + COMMON_WORDS
    return "\n\n".join(random_paragraph(words, rng, sentences=rng.randint(3, 6)) for _ in range(2))


def pad_to_size(content: str, target_bytes: int, rng: random.Random) -> str:
    current_bytes = len(content.encode("utf-8"))
    if current_bytes >= target_bytes:
        return trim_to_size(content, target_bytes)

    filler_words = COMMON_WORDS + ["filler", "padding", "repeat", "content"]
    while current_bytes < target_bytes:
        paragraph = random_paragraph(filler_words, rng, sentences=3)
        content = f"{content}\n\n{paragraph}"
        current_bytes = len(content.encode("utf-8"))
    return trim_to_size(content, target_bytes)


def trim_to_size(content: str, target_bytes: int) -> str:
    while len(content.encode("utf-8")) > target_bytes:
        content = content[:-1]
    return content


def render_note(
    *,
    template: str,
    category: str,
    secondary: str | None,
    size_kb: int,
    rng: random.Random,
) -> tuple[str, str]:
    title = build_title(category, rng)
    words = CATEGORY_WORDS[category] + COMMON_WORDS
    fields = {
        "title": title,
        "date": random_date(rng),
        "tags": choose_tags(category, rng),
        "body": note_body(category, rng),
        "bullets": build_bullets(words, rng, count=rng.randint(3, 6)),
        "links": build_links(category, rng, count=rng.randint(2, 4)),
        "code_block": build_code_block(category, rng),
        "mixed_section": build_mixed_section(category, secondary or category, rng)
        if secondary
        else "",
        "edge_case_block": build_edge_case_block(rng),
    }
    content = template.format_map(fields)
    return pad_to_size(content.strip(), size_kb * 1024, rng), title


def generate_notes(
    *,
    count: int,
    categories: list[str],
    min_kb: int,
    max_kb: int,
    templates: dict[str, str],
    out_dir: Path,
    ambiguous_rate: float,
    rng: random.Random,
) -> list[NoteSpec]:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[NoteSpec] = []

    for idx in range(count):
        category = rng.choice(categories)
        ambiguous = rng.random() < ambiguous_rate
        secondary = None
        if ambiguous:
            secondary = rng.choice([c for c in categories if c != category])
        size_kb = rng.randint(min_kb, max_kb)
        content, title = render_note(
            template=templates[category],
            category=category,
            secondary=secondary,
            size_kb=size_kb,
            rng=rng,
        )
        slug = slugify(title)
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}-{category}-{slug}-{idx:04d}.md"
        (out_dir / filename).write_text(content, encoding="utf-8")
        manifest.append(
            NoteSpec(
                index=idx,
                category=category,
                size_kb=size_kb,
                ambiguous=ambiguous,
                filename=filename,
            )
        )

    return manifest


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)

    categories = CATEGORIES
    if args.categories:
        categories = [c.strip() for c in args.categories.split(",") if c.strip()]
    invalid = [c for c in categories if c not in CATEGORIES]
    if invalid:
        raise SystemExit(f"Invalid categories: {', '.join(invalid)}")
    if args.min_kb <= 0 or args.max_kb <= 0 or args.min_kb > args.max_kb:
        raise SystemExit("Invalid size range: min-kb/max-kb")

    templates = load_templates(args.templates_dir)
    manifest = generate_notes(
        count=args.count,
        categories=categories,
        min_kb=args.min_kb,
        max_kb=args.max_kb,
        templates=templates,
        out_dir=args.out_dir,
        ambiguous_rate=args.ambiguous_rate,
        rng=rng,
    )

    if args.manifest:
        payload = [note.__dict__ for note in manifest]
        args.manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
