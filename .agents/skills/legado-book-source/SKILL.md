---
name: legado-book-source
description: Creates, repairs, explains, and validates Legado (阅读) book-source JSON for HTML pages or JSON APIs. Use when a user asks to 写书源、制作阅读书源、调试 Legado 规则、迁移网站解析、配置搜索/详情/目录/正文/发现/登录规则，或检查书源 JSON。
---

# Legado Book Source

## Quick start

1. Identify the target site, one searchable title, one detail URL, and whether login is required.
2. Build the smallest complete path: search → detail → table of contents → chapter content.
3. Prefer declarative selectors; introduce JavaScript only for request signing, dynamic URLs, state, or data transformation.
4. Start from [assets/source-template.json](assets/source-template.json).
5. Validate before delivery:

```powershell
python scripts/validate_book_source.py path/to/source.json
```

## Choose references

- New source: read [references/WORKFLOW.md](references/WORKFLOW.md), [references/SCHEMA.md](references/SCHEMA.md), and [references/RULE_SYNTAX.md](references/RULE_SYNTAX.md).
- Complex login/API/JavaScript source: also read [references/EXAMPLE_ANALYSIS.md](references/EXAMPLE_ANALYSIS.md).
- Documentation/version questions: consult [references/SOURCES.md](references/SOURCES.md) and verify against the user's installed Legado version when behavior differs.
- Validation-only request: run the validator first, then inspect only the reported sections.

## Required workflow

1. **Scope** — record target URL, source type, required features, login state, and expected output path. Infer safe defaults instead of blocking on minor omissions.
2. **Reconnaissance** — inspect HTML and network responses; record request method, parameters, headers/cookies, pagination, encoding, redirects, and stable fields.
3. **Design** — map endpoints and selectors in a field table before writing JSON.
4. **Implement vertically** — make one known book work end-to-end before adding discovery, pagination variants, login UI, variables, or formatting.
5. **Validate** — parse JSON, run the bundled validator, then test import and each Legado debug stage.
6. **Deliver** — provide the JSON path, supported features, test evidence, assumptions, and unresolved site/version constraints.

## Quality rules

- Use UTF-8 JSON and preserve correct escaping inside regex and JavaScript strings.
- Prefer stable IDs, semantic classes, JSON keys, and API fields over positional selectors.
- Keep URL construction in URL rules and parsing in rule groups; avoid duplicated JavaScript.
- Make pagination explicit; verify page 1 and at least one later page.
- Normalize relative URLs and verify cover, book, TOC, chapter, and next-page links independently.
- Treat empty results as data-shape or authentication failures until proven otherwise.
- Never invent selectors, tokens, signatures, or successful test results.

## Safety

Work only with public content or access the user is authorized to use. Do not bypass paywalls, DRM, CAPTCHA, rate limits, or access controls. Do not collect credentials; use Legado login mechanisms and redact cookies/tokens from reports. Preserve attribution and license notices when adapting existing sources.
