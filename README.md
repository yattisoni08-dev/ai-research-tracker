# AI Research Tracker

A living AI research database and editorial briefing. The site has two views: **Newly Published** (new items from the configured source list, each linked to its original publication) and **The Bigger Picture** (cross-source synthesis, major debates, connections and a watchlist).

## Research coverage
The source registry is maintained in `scripts/daily_research.py` and stored in `data/research-db.json`. It covers Razorpay Engineering and Razorpay AI posts first, then AI labs, builders and developer tools, Stripe, global payment companies, selected practitioners, research papers and technical communities.

The collector checks RSS/Atom feeds and Google News RSS searches for sources without reliable feeds. Search coverage of X is best-effort and is not a complete archive of posts. Every published item links to a URL returned by a source feed or search result. Previously collected URLs are deduplicated.

## Persistent data
- `data/research-db.json`: source registry, cumulative item archive, debate histories, daily run log and current briefing.
- `data/tracker.json`: compact data file consumed by the public website.

The database accumulates indefinitely. There is no closing date or automatic expiry. The daily run uses the previous run timestamp and known URLs to identify new publications.

## Daily automation
GitHub Actions runs daily at approximately 08:00 Asia/Kolkata, indefinitely, and can also be started manually from Actions → Daily AI Research → Run workflow. Each run collects source material, generates editorial analysis with the OpenAI API, updates the archive and publishes the website data.

Required GitHub Actions secrets:
- `OPENAI_API_KEY`
- `NETLIFY_BUILD_HOOK_URL` (optional if Netlify already deploys automatically on GitHub commits)

Optional repository variable:
- `OPENAI_MODEL` (default: `gpt-4o-mini`).

## Local preview
Open `index.html` with a local static server, for example `python -m http.server 8000`.
