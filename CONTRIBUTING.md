# Contributing

Thanks for improving Content Lens.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,youtube]'
pytest
ruff check .
```

## Contribution types

- New source apps: X, Reddit, podcasts, webpages, PDFs.
- Better processors: diarization providers, OCR, topic segmentation, claim extraction.
- Reporters: HTML, Obsidian, JSONL, MCP tool outputs.

## Rules

- Keep extraction and interpretation separate.
- Add fixtures/tests for parsing and artifact shape changes.
- Do not require secrets for unit tests.
- Mark inferred speaker identities with confidence and evidence.
