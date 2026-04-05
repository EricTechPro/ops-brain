---
name: sync-project
description: Smart sync a project's emails from Gmail — fetches all emails under their Gmail label, deduplicates against what's already logged, validates existing entries, groups by thread, and routes attachments. For ongoing syncs after initial onboarding.
---

**Usage:** `/sync-project <project-name>`

## Steps

### 1. Pick project + read config

> [!sub-workflow] Project Picker
> Read and execute `shared/project-picker.md`
> Params: allow_new = false

> [!sub-workflow] Read Project Context
> Read and execute `shared/read-project-context.md`
> Input: project-name from picker

From the context, use `gmail_config` (label name, synced message IDs, last sync date).
If no `## Gmail Sync` section exists in overview.md, ask for the Gmail label name and create the section.

### 2. Fetch all emails from label
- Run: `python3 scripts/gmail_sync.py label <label> --max-results 100 --download-attachments /tmp/gmail-sync`
- Parse JSON output — each message has `id`, `thread_id`, `subject`, `body`, `direction`, `from`, `attachments`

### 3. Deduplicate + validate
- Compare each fetched message `id` against synced IDs from step 1
- **New messages** (not in synced list) → queue for logging
- **Existing messages** (already synced) → validate against `conversation-log.md`. If a summary or detail doesn't match Gmail data, flag to user: "Discrepancy in thread X — vault says Y, Gmail says Z"
- If zero new + no discrepancies → report "Already up to date" and stop

### 4. Present to user before writing
Show summary and wait for confirmation:
```
Found N new emails not in conversation log:
- 🧵 Re: Subject (thread:abc123) — Sender on YYYY-MM-DD
- 🧵 Re: Subject (thread:def456) — Sender on YYYY-MM-DD
```
Includes emails from any date — old emails labeled later are still caught.

### 5. Write to conversation log + extract action items

For each new message, use the shared log module:

> [!sub-workflow] Log and Extract
> Read and execute `shared/log-and-extract.md`
> Input: project-name, entry-type = email-sent or email-received (based on direction), summary from email body
> Thread: subject and thread_id for thread grouping

Use `[[wikilinks]]` for any routed files (attachments in `constants/`, deliverables, etc.)

### 6. Route attachments + links

> [!sub-workflow] Route Files
> Read and execute `shared/route-files.md`
> Input: project-name, files = downloaded attachments from /tmp/gmail-sync

Additionally: extract URLs from email bodies → append to `projects/<name>/links.md` under appropriate heading.

### 7. Update sync state
- Append new message IDs to synced list in `overview.md`
- Update "Last synced" timestamp

### 8. Clean up + report
- Remove `/tmp/gmail-sync/`
- Output:
```
Synced <project>: N new emails across M threads
- 🧵 Thread subject (X messages)
Attachments: N → constants/, N → inbox/
Links: N → links.md
Action items: N added
```
