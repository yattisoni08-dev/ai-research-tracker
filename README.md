# AI Research Tracker

A responsive, read-only editorial website for daily AI research and industry intelligence. The daily edition is generated from source feeds and published as static JSON.

## Local preview
Open `index.html` with a local static server (for example, `python -m http.server 8000`).

## Daily automation
A GitHub Actions workflow runs at 08:00 Asia/Kolkata (02:30 UTC). It reads configured RSS/Atom feeds, filters recent items, asks the OpenAI API to produce a cited editorial briefing, updates `data/tracker.json`, commits the change, and triggers a Netlify build hook.

Required GitHub Actions secrets:
- `OPENAI_API_KEY`: API key for the OpenAI API.
- `NETLIFY_BUILD_HOOK_URL`: Netlify build hook URL for the connected site.

Optional repository variable:
- `OPENAI_MODEL`: model name available to your API account (default: `gpt-5-mini`).

Run manually from Actions → Daily AI Research → Run workflow. The public site is read-only; edits happen through the repository and scheduled workflow.
