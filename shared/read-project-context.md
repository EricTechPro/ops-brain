# Read Project Context

Load a project's key files and return structured context for use by other workflows.

## Input
- `<project-name>` — the project folder name under `projects/`

## Steps

1. **Read overview.md** — `projects/<project-name>/overview.md`. If the file is missing, return empty context for all overview fields and set `overview_missing = true` — the calling skill decides how to handle this (e.g., `/respond` needs contacts, so it should ask the user directly). Extract:
   - **contacts**: name, email, phone, role for each person listed
   - **communication_prefs**: preferred timezone, channel (email/slack/phone), tone
   - **gmail_config**: from `## Gmail Sync` section — label name, list of synced message IDs, last sync timestamp. If `## Gmail Sync` exists but is malformed (missing Label, or synced IDs not parseable), return what's available and set `gmail_config_partial = true` with a description of what's wrong — don't silently skip.
   - **project_info**: client name, industry, website, scope, contract type, pricing

2. **Read conversation-log.md** — `projects/<project-name>/conversation-log.md`. If missing, return empty entries/actions and set `log_missing = true`. Extract:
   - **recent_entries**: the last 10 log entries (any type — 📧, 📞, 🔄, etc.)
   - **pending_actions**: all unchecked `- [ ]` items from `## Action Items`
   - **completed_actions**: all checked `- [x]` items from `## Completed` (last 5 only)
   - **last_activity_date**: date of the most recent log entry

3. **Read frontmatter** — from overview.md or conversation-log.md:
   - **project_status**: active / blocked / pending / complete (from `#status/*` tag)
   - **visibility**: internal / shared (from `#visibility/*` tag)

## Returns
All extracted fields above, organized as structured context. The calling skill decides which fields it needs — not all fields are required by every consumer.
