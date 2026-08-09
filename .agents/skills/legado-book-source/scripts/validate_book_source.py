#!/usr/bin/env python3
"""Static validator for Legado book-source JSON files.

No third-party dependencies are required. This checks JSON structure and common
cross-field mistakes; it cannot replace importing and debugging in Legado.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, location: str, message: str) -> None:
        self.errors.append(f"{location}: {message}")

    def warn(self, location: str, message: str) -> None:
        self.warnings.append(f"{location}: {message}")


def nonblank(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def walk_strings(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from walk_strings(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk_strings(item, f"{path}[{index}]")


def validate_embedded_json(
    source: dict[str, Any], field_name: str, location: str, report: Report
) -> None:
    value = source.get(field_name)
    if not nonblank(value):
        return
    stripped = value.lstrip()
    if not stripped.startswith(("{", "[")):
        return
    try:
        json.loads(value)
    except json.JSONDecodeError as exc:
        report.error(
            f"{location}.{field_name}",
            f"looks like embedded JSON but fails at line {exc.lineno}, "
            f"column {exc.colno}: {exc.msg}",
        )


def require_rule_fields(
    source: dict[str, Any],
    group_name: str,
    fields: tuple[str, ...],
    location: str,
    report: Report,
) -> None:
    group = source.get(group_name)
    if not isinstance(group, dict):
        report.error(f"{location}.{group_name}", "must be an object")
        return
    for field_name in fields:
        if not nonblank(group.get(field_name)):
            report.error(f"{location}.{group_name}.{field_name}", "must not be blank")


def validate_source(source: Any, index: int, report: Report) -> None:
    location = f"$[{index}]"
    if not isinstance(source, dict):
        report.error(location, "source entry must be an object")
        return

    display_name = source.get("bookSourceName")
    if nonblank(display_name):
        location = f"$[{index}]({display_name.strip()})"
    else:
        report.error(f"$[{index}].bookSourceName", "must be a non-empty string")

    source_type = source.get("bookSourceType")
    if not isinstance(source_type, int) or isinstance(source_type, bool):
        report.error(f"{location}.bookSourceType", "must be an integer")
    elif source_type not in (0, 1, 2, 3):
        report.warn(f"{location}.bookSourceType", "usual values are 0, 1, 2, or 3")

    source_url = source.get("bookSourceUrl")
    if not nonblank(source_url):
        report.error(f"{location}.bookSourceUrl", "must be a non-empty string")
    else:
        parsed = urlparse(source_url.strip())
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            report.warn(
                f"{location}.bookSourceUrl",
                "is not a complete HTTP(S) URL; confirm relative URL resolution",
            )

    for boolean_field in ("enabled", "enabledExplore", "enabledCookieJar"):
        if boolean_field in source and not isinstance(source[boolean_field], bool):
            report.error(f"{location}.{boolean_field}", "must be a boolean")

    timestamp = source.get("lastUpdateTime")
    if timestamp is not None:
        if not isinstance(timestamp, (int, float)) or isinstance(timestamp, bool):
            report.error(f"{location}.lastUpdateTime", "must be a millisecond timestamp")
        elif timestamp <= 0:
            report.warn(f"{location}.lastUpdateTime", "has not been set")
        else:
            now_ms = datetime.now(timezone.utc).timestamp() * 1000
            if timestamp > now_ms + 24 * 60 * 60 * 1000:
                report.warn(
                    f"{location}.lastUpdateTime",
                    "is in the future; check timestamp units or system time",
                )

    if nonblank(source.get("searchUrl")):
        require_rule_fields(
            source,
            "ruleSearch",
            ("bookList", "name", "bookUrl"),
            location,
            report,
        )
    else:
        report.warn(f"{location}.searchUrl", "is blank; normal search will not work")

    if source_type in (0, 1, 2):
        require_rule_fields(
            source,
            "ruleToc",
            ("chapterList", "chapterName", "chapterUrl"),
            location,
            report,
        )
        require_rule_fields(source, "ruleContent", ("content",), location, report)
    elif source_type == 3:
        book_info = source.get("ruleBookInfo")
        if not isinstance(book_info, dict) or not nonblank(book_info.get("downloadUrls")):
            report.warn(
                f"{location}.ruleBookInfo.downloadUrls",
                "file sources usually need a download URL rule",
            )

    book_info = source.get("ruleBookInfo")
    if not isinstance(book_info, dict):
        report.error(f"{location}.ruleBookInfo", "must be an object")
    elif not any(nonblank(value) for value in book_info.values()):
        report.warn(
            f"{location}.ruleBookInfo",
            "contains no detail rules; confirm list data and TOC URL are sufficient",
        )

    if source.get("enabledExplore") is True and nonblank(source.get("exploreUrl")):
        explore_rule = source.get("ruleExplore")
        if not isinstance(explore_rule, dict):
            report.error(f"{location}.ruleExplore", "must be an object")
        elif not explore_rule:
            report.warn(
                f"{location}.ruleExplore",
                "is empty; confirm discovery reuses search rules or opens details directly",
            )
        else:
            for field_name in ("bookList", "name", "bookUrl"):
                if not nonblank(explore_rule.get(field_name)):
                    report.warn(
                        f"{location}.ruleExplore.{field_name}",
                        "is blank; valid only when discovery intentionally reuses other rules",
                    )

    for embedded_field in ("header", "loginUi", "exploreUrl"):
        validate_embedded_json(source, embedded_field, location, report)

    for string_path, text in walk_strings(source, location):
        if re.search(r"\bTODO\b", text, re.IGNORECASE):
            report.warn(string_path, "still contains TODO placeholder text")
        if text.count("<js>") != text.count("</js>"):
            report.error(string_path, "has unbalanced <js> and </js> tags")
        if re.search(
            r'''(?i)["']Authorization["']\s*:\s*["']Bearer\s+[A-Za-z0-9._~+/=-]{20,}''',
            text,
        ):
            report.warn(string_path, "may contain a hard-coded Bearer token")
        if re.search(r'''(?i)["']Cookie["']\s*:\s*["'][^"']{20,}''', text):
            report.warn(string_path, "may contain a hard-coded Cookie")


def load_sources(path: Path, report: Report) -> list[Any]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        report.error(str(path), f"is not valid UTF-8: {exc}")
        return []
    except OSError as exc:
        report.error(str(path), f"cannot be read: {exc}")
        return []

    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        report.error(
            str(path),
            f"JSON fails at line {exc.lineno}, column {exc.colno}: {exc.msg}",
        )
        return []

    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        if not value:
            report.error(str(path), "source array is empty")
        return value
    report.error(str(path), "root value must be a source object or an array of sources")
    return []


def validate_duplicates(sources: list[Any], report: Report) -> None:
    for field_name in ("bookSourceName", "bookSourceUrl"):
        seen: dict[str, int] = {}
        for index, source in enumerate(sources):
            if not isinstance(source, dict) or not nonblank(source.get(field_name)):
                continue
            value = source[field_name].strip()
            if value in seen:
                report.warn(
                    f"$[{index}].{field_name}",
                    f"duplicates $[{seen[value]}]: {value}",
                )
            else:
                seen[value] = index


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Statically validate a Legado book-source JSON file."
    )
    parser.add_argument("json_file", type=Path, help="book-source JSON file")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="return a non-zero status when warnings exist",
    )
    args = parser.parse_args()

    report = Report()
    sources = load_sources(args.json_file, report)
    for index, source in enumerate(sources):
        validate_source(source, index, report)
    validate_duplicates(sources, report)

    print(f"File: {args.json_file}")
    print(f"Sources: {len(sources)}")
    print(f"Errors: {len(report.errors)}; warnings: {len(report.warnings)}")
    for message in report.errors:
        print(f"ERROR   {message}")
    for message in report.warnings:
        print(f"WARNING {message}")

    if report.errors or (args.strict and report.warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
