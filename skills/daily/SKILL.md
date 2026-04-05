---
name: daily
description: Generate a live daily briefing by scanning the vault in real-time. Do NOT use cached or static data.
---

> **Strictly read-only and local-only.** Never call external APIs, trigger Gmail syncs, or run scripts. Reads only local vault files. Run `/sync-project` first to get fresh email data.

## Steps

1. **Project Dashboard + Action Items** — For each project folder in `projects/`:

> [!sub-workflow] Read Project Context
> Read and execute `shared/read-project-context.md`
> Input: each project-name in sequence

   From each project's context, extract:
   - `pending_actions` — all unchecked action items
   - `last_activity_date` — most recent log entry date
   - Flag projects with no entries in 14+ days with ⚠️

   Build project table:
   | Project | Last Activity | Pending Actions | Stale? |

   Then group all collected action items by @handle:
   - **@eric** — items I need to do
   - **@contact** — items I'm waiting on from contacts
   - **Other @handles** — delegated items
   Show due dates. Flag overdue items (past today's date) with 🔴.

3. **Inbox Check** — List everything in `inbox/`. Show file count, names, and how long each has been sitting there. If items exist, suggest running `/onboard`.

4. **Today's Note** — Check if `daily/{{today's date}}-daily.md` exists. If yes, show it. If no, offer to create one.

Output everything in Obsidian-flavored markdown with [[wikilinks]] to the source files.
