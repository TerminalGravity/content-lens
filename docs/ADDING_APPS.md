# Adding a source app

1. Create `src/content_lens/apps/<name>.py`.
2. Implement `ContentApp.can_handle(url)` and `ContentApp.extract(...)`.
3. Return an `ExtractionResult` with metadata, transcript turns, visual observations, and asset paths.
4. Register the app in `AppRegistry`.
5. Add tests that do not require live network access. Use fixtures.

## App quality bar

- Do not invent missing transcript or speaker identity.
- Preserve source URLs and timestamps.
- Store raw assets under `assets/`; normalized artifacts at the run root.
- Keep credentials optional and out of artifacts.
- Report confidence/evidence for inferred identities.
