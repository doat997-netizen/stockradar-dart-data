# Stock Radar v150 – locally verified QA (2026-11-13)

- Original application: v149, v150 patch preserves the 35 routes and pre-existing static HTML IDs.
- Local Chromium tests: **25/25** desktop 1440px / mobile 390px / 320px passed.
- Date-filter / 35-route regression checks: **41/41** passed with injected test fixtures.
- Main dashboard: chart + today's filings; earlier dates are not substituted if today is empty.
- Korea DART: Asia/Seoul calendar day from the public cache. US SEC: America/New_York day from queried issuer records. These sources do **not** guarantee full-market coverage or real-time publication.
- Data records: legacy localStorage and IndexedDB opening call counts unchanged.
- External data fetching was blocked during browser QA. Actual live SEC Worker, DART production CORS, operating site state and personal backups are **not verified**.
- The companion GitHub workflow validates only `data/dart_cache.json`. It does **not** run v150 UI tests or deploy the HTML application.
- Do not claim an operational GitHub Actions run succeeded until an actual workflow execution is observed.
