# Architecture

Content Lens has four layers:

1. **Apps**: source-specific extractors such as YouTube, future X, Reddit, podcasts, webpages.
2. **Processors**: source-agnostic enrichment such as VTT normalization, diarization alignment, speaker profiling, topic chunking, OCR/vision observations.
3. **Canonical artifacts**: JSON files with stable shapes so other agents/apps can consume results.
4. **Reporters**: Markdown/HTML/LLM-ready outputs.

## Canonical timeline

Every app should eventually produce turns like:

```json
{"start":12.4,"end":18.2,"speaker":"SPEAKER_01","text":"..."}
```

Diarization, OCR, claims, and topics should attach to this timeline rather than living as isolated summaries.
