# Hill Green Insights automation

## What it does
- Runs daily at 07:15 IST (01:45 UTC) and can also be started manually.
- Collects recent stories from the RSS feeds listed in `config/sources.json`.
- Uses the OpenAI API to create short summaries based only on each feed's headline and excerpt.
- Keeps the original publisher, publication date and source URL with every summary.
- Deduplicates by canonical feed URL and retains up to 60 recent items.
- Publishes the generated JSON dataset to GitHub Pages through the normal repository deployment.

## Required GitHub configuration
1. Open repository Settings → Secrets and variables → Actions.
2. Create a repository secret named `OPENAI_API_KEY` with an OpenAI API key.
3. Ensure GitHub Actions is enabled.
4. Under Settings → Actions → General → Workflow permissions, allow the workflow to read and write repository contents.
5. Under Settings → Pages, confirm the site is deployed from the `main` branch (or the branch configured for Pages).

The script can still collect and display feed excerpts if the API key is not configured, but AI summaries require the secret. API usage is billed separately by OpenAI.

## Run or monitor
- Actions → Refresh Hill Green Insights → Run workflow.
- Check the run logs for source-feed errors and summary fallback notices.
- The scheduled run is daily; GitHub may delay scheduled starts during high load.

## Editorial and usage notes
- Cards link to the original publisher. The site does not republish full articles.
- RSS feeds can change, move or restrict access. Review feed health periodically.
- Automated summaries are informational. Verify important details against the linked source.
- Add or remove feeds by editing `config/sources.json`.
- To change the schedule, edit the cron expression in `.github/workflows/insights.yml`.
