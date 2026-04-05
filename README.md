# ops-brain

A Claude Code plugin for project managers handling multiple projects. Provides 5 skills for daily briefings, conversation logging, email responses, Gmail sync, and project onboarding — all backed by an Obsidian vault as your second brain.

## Installation

```bash
claude plugin marketplace add github:EricTechPro/ops-brain
claude plugin install ops-brain
```

---

## Skills

| Skill | Command | What it does |
|-------|---------|-------------|
| Daily | `/daily` | Morning briefing — scans all projects for pending tasks, recent activity, and inbox status |
| Log | `/log` | Adds a timestamped entry to a project's conversation log and extracts action items |
| Onboard | `/onboard` | Sets up new or existing projects — imports from Gmail, files, or pasted text |
| Respond | `/respond` | Crafts an email as copyable HTML, opens in browser, logs after sending, deletes file |
| Sync Project | `/sync-project` | Fetches emails from a Gmail label, dedupes, threads, routes attachments |

---

## How Each Skill Works

### `/daily` — Morning Dashboard

> Read-only. No external calls. No file writes.

**Flow:**
```
╔═══════════════════╗     ╔═══════════════════╗     ╔═══════════════════╗
║  Scan all         ║────▶║  Build project     ║────▶║  Group actions    ║
║  projects/*/      ║     ║  table + flag      ║     ║  by @handle       ║
║  conversation-    ║     ║  stale (14+ days)  ║     ║  flag overdue 🔴  ║
║  log.md           ║     ╚═══════════════════╝     ╚════════╤══════════╝
╚═══════════════════╝                                        │
                          ╔═══════════════════╗     ╔════════▼══════════╗
                          ║  Check/offer      ║◀────║  List inbox/      ║
                          ║  today's daily    ║     ║  unprocessed      ║
                          ║  note             ║     ║  files            ║
                          ╚═══════════════════╝     ╚═══════════════════╝
```

**Sub-workflows called:** None — reads vault files directly

**Example output:**
```
## Project Dashboard
| Project        | Last Activity | Pending Actions | Stale? |
|---------------|--------------|-----------------|--------|
| acme-corp      | 2026-04-03   | 3               |        |
| greenfield-app | 2026-03-18   | 1               | ⚠️     |

## Action Items
### @eric
- [ ] Send revised quote to Sarah — due 2026-04-05
- [ ] Review contract draft — due 2026-04-07 🔴

### @contact
- [ ] Sarah to confirm budget — due 2026-04-04

## Inbox (2 files)
- pitch-deck.pdf (3 days old)
- meeting-notes.txt (1 day old)
→ Run /onboard to process these
```

---

### `/log` — Add Conversation Entry

**Flow:**
```
╔═══════════════╗     ╔═══════════════╗     ╔═══════════════╗     ╔═══════════════╗
║ 📂 project-   ║────▶║ Ask: what     ║────▶║ 📝 log-and-  ║────▶║ Extract       ║
║ picker        ║     ║ happened?     ║     ║ extract       ║     ║ action items  ║
║               ║     ║ type? summary?║     ║ write entry   ║     ║ add to log    ║
╚═══════════════╝     ╚═══════════════╝     ╚═══════════════╝     ╚══════╤════════╝
                                                                          │
                                                                 ╔════════▼════════╗
                                                                 ║ Any items done? ║
                                                                 ║ [ ] → [x] ✓    ║
                                                                 ╚═════════════════╝
```

**Sub-workflows called:** `project-picker` → `log-and-extract`

**Example:**
```
> /log acme-corp

What happened?
> Call with Sarah about Q2 deliverables

Summary?
> Agreed on new timeline. Sarah will send updated SOW by Friday.

✓ Entry added to conversation-log.md:
  #### 2026-04-04
  - 📞 **Call**: Q2 deliverables — Agreed on new timeline, SOW by Friday

✓ Action items extracted:
  - [ ] @contact Sarah to send updated SOW — due 2026-04-11

Any existing items completed?
> Yes — "Review contract draft"
  - [x] @eric Review contract draft — done 2026-04-04 ✓
```

---

### `/onboard` — Import & Set Up a Project

**Flow:**
```
╔═══════════════╗     ╔══════════════════════╗
║ 📂 project-   ║────▶║ Collect sources:     ║
║ picker        ║     ║  Gmail label?        ║
║ (allow new)   ║     ║  Local files/folders?║
╚═══════════════╝     ║  Pasted text?        ║
                      ╚═══════════╤══════════╝
                      ┌───────────┼───────────┐
                      ▼           ▼           ▼
               ╔════════════╗╔════════════╗╔════════════╗
               ║ A: Gmail   ║║ B: Local   ║║ C: Pasted  ║
               ║ gmail_sync ║║ 📦 route-  ║║ detect     ║
               ║ .py fetch  ║║ files      ║║ type +     ║
               ║ + thread   ║║ by type    ║║ route      ║
               ╚═════╤══════╝╚═════╤══════╝╚═════╤══════╝
                     └─────────────┼─────────────┘
                                   ▼
               ╔════════════════════════════════════╗
               ║ Conflict check                     ║
               ║ (dupes / contradictions / ambiguous)║
               ╚════════════════╤═══════════════════╝
                                ▼
               ╔════════════════════════════════════╗
               ║ Auto-extract profile → overview.md  ║
               ║ (new projects only)                 ║
               ╚════════════════╤═══════════════════╝
                                ▼
               ╔════════════════════════════════════╗
               ║ 📝 log-and-extract                  ║
               ║ "Project onboarded" entry           ║
               ╚════════════════╤═══════════════════╝
                                ▼
               ╔════════════════════════════════════╗
               ║ Key Events Report + next actions    ║
               ╚════════════════════════════════════╝
```

**Sub-workflows called:** `project-picker` → `route-files` → `log-and-extract`

**Scripts:** `python3 scripts/gmail_sync.py` (Gmail path only)

**Example output:**
```
## Onboarding Report: acme-corp

### Key Events
- Started: 2026-01-15 (earliest email found)
- Contract: Retainer — $5,000/mo
- Current Status: Active, mid-Q2 deliverables

### Timeline
- 2026-01-15 — First contact via email
- 2026-02-01 — Contract signed
- 2026-04-03 — Most recent: call re Q2 timeline

### Imported
- 24 emails (8 threads) · 3 files · 12 links · 4 action items

What's next?
1. Import more data
2. Draft an email → /respond
3. Set up recurring sync → /sync-project
4. Done for now
```

---

### `/respond` — Draft & Send Email

**Flow:**
```
╔═══════════════╗     ╔═══════════════╗     ╔═══════════════╗
║ 📂 project-   ║────▶║ Ask: reply to ║────▶║ 📖 read-      ║
║ picker        ║     ║ what? tone?   ║     ║ project-      ║
║               ║     ║ key points?   ║     ║ context       ║
╚═══════════════╝     ╚═══════════════╝     ╚══════╤════════╝
                                                    ▼
                                            ╔═══════════════╗
                                            ║ Load style    ║
                                            ║ guide (if biz ║
                                            ║ cooperation)  ║
                                            ╚══════╤════════╝
                                                    ▼
╔═══════════════╗     ╔═══════════════╗     ╔═══════════════╗
║ Delete HTML   ║◀────║ User: "Sent!" ║◀────║ Generate HTML ║
║ file + done   ║     ║               ║     ║ → responses/  ║
╚═══════════════╝     ║ 📝 log-and-  ║     ║ open browser  ║
                      ║ extract       ║     ╚═══════════════╝
                      ╚═══════════════╝
```

**Sub-workflows called:** `project-picker` → `read-project-context` → `log-and-extract`

**File created:** `projects/<name>/responses/YYYY-MM-DD-topic.html` (temporary — deleted after sending)

**The HTML file includes:**
- "Copy to clipboard" button (top-right corner)
- Meta section with To / Subject / Date (visible but not copied)
- Clean email body using only `<p>`, `<b>`, `<br>`, `<ul>`, `<li>`
- Hidden strategy notes as `<!-- HTML comments -->`

**Example:**
```
> /respond acme-corp

What are you responding to?
> Sarah asked about the Q2 timeline adjustment

Key points?
> Confirm new dates, mention we'll absorb the delay, ask for updated SOW

Tone?
> Professional but warm

[Draft shown for review]
[HTML file opened in browser — click "Copy to clipboard" → paste into Gmail]

Have you sent it?
> Yes

✓ Logged: 📧 Email sent: Q2 timeline confirmation
✓ Action item: @contact Sarah to send updated SOW — due 2026-04-11
✓ Deleted: responses/2026-04-04-q2-timeline.html
```

---

### `/sync-project` — Pull Emails from Gmail

**Flow:**
```
╔═══════════════╗     ╔═══════════════╗     ╔═══════════════════╗
║ 📂 project-   ║────▶║ 📖 read-      ║────▶║ Run gmail_sync.py ║
║ picker        ║     ║ project-      ║     ║ fetch from label  ║
║               ║     ║ context       ║     ║ + download        ║
╚═══════════════╝     ║ (Gmail config)║     ║ attachments       ║
                      ╚═══════════════╝     ╚════════╤══════════╝
                                                      ▼
╔═══════════════════╗  ╔═══════════════╗    ╔═════════════════════╗
║ Update sync state ║◀─║ 📦 route-    ║◀───║ Dedupe against      ║
║ in overview.md    ║  ║ files        ║    ║ synced IDs          ║
║ cleanup /tmp      ║  ║ (attachments ║    ║ → show new emails   ║
║ print report      ║  ║ + URLs →     ║    ║ → user confirms     ║
╚═══════════════════╝  ║ links.md)    ║    ║ → 📝 log-and-extract║
                       ╚══════════════╝    ║   per email (threaded)║
                                           ╚═══════════════════════╝
```

**Sub-workflows called:** `project-picker` → `read-project-context` → `log-and-extract` (per email) → `route-files`

**Script:** `python3 scripts/gmail_sync.py label <label> --max-results 100 --download-attachments /tmp/gmail-sync`

**Example output:**
```
Synced acme-corp: 5 new emails across 2 threads
- 🧵 Re: Q2 Timeline (3 messages)
- 🧵 Invoice #1042 (2 messages)
Attachments: 1 → constants/ (invoice-1042.pdf)
Links: 3 → links.md
Action items: 2 added
```

---

## Recommended Usage Order

```
╔═══════════╗     ╔════════════════╗     ╔═════════╗     ╔═════════╗     ╔═══════════╗
║ /onboard  ║────▶║ /sync-project  ║────▶║ /daily  ║────▶║  /log   ║────▶║ /respond  ║
║           ║     ║                ║     ║         ║     ║         ║     ║           ║
║ First-time║     ║ Pull new       ║     ║ Morning ║     ║ After   ║     ║ Reply to  ║
║ setup     ║     ║ emails         ║     ║ check-in║     ║ meetings║     ║ emails    ║
╚═══════════╝     ╚════════════════╝     ╚═════════╝     ╚═════════╝     ╚═══════════╝
  once              periodically          each morning     as needed       as needed
```

---

## Shared Sub-Workflows

Internal modules in `shared/` used by the skills above. Not user-invokable.

| Module | Used By | What it does |
|--------|---------|-------------|
| `project-picker` | all 5 skills | Lists projects from `projects/`, resolves user selection, optionally creates new project with full folder structure |
| `read-project-context` | `/respond`, `/sync-project` | Reads `overview.md` + `conversation-log.md` → returns contacts, Gmail config, recent entries, pending actions |
| `log-and-extract` | `/log`, `/respond`, `/sync-project`, `/onboard` | Writes an emoji-formatted entry under the correct date heading, scans for action items, adds them to `## Action Items` |
| `route-files` | `/onboard`, `/sync-project` | Classifies files by content/filename and routes them to `constants/`, `links.md`, `shared/deliverables/`, or conversation log |

**How sub-workflows connect to skills:**
```
/daily ──────────────────────────────────────── (no sub-workflows, reads directly)

/log ──────── project-picker → log-and-extract

/onboard ──── project-picker → route-files → log-and-extract

/respond ──── project-picker → read-project-context → log-and-extract

/sync-project ─ project-picker → read-project-context → log-and-extract → route-files
```

---

## Required Vault Structure

Your Obsidian vault needs this layout:

```
your-vault/
├── inbox/                  ← Unprocessed dumps (PDFs, text, CSVs, screenshots)
├── daily/                  ← Dated notes and briefings
├── projects/
│   └── [project-name]/
│       ├── overview.md            ← Project + client profile, contacts
│       ├── conversation-log.md    ← Source of truth — all interactions
│       ├── links.md               ← Categorized URL library
│       ├── constants/             ← Contracts, agreements, invoices
│       ├── responses/             ← Temporary email drafts (auto-deleted)
│       └── shared/
│           └── deliverables/      ← Quotes, proposals, work product
├── templates/              ← Reusable note templates
├── archives/               ← Completed projects
├── scripts/                ← gmail_sync.py for Gmail integration
└── team.md                 ← Global handle → name → role lookup
```

## Gmail Integration

Requires `scripts/gmail_sync.py` with OAuth2 (read-only access). Used by `/sync-project` and `/onboard` for email import. See the vault's `scripts/` directory for setup.

## File Locations

```
.claude/skills/ops-brain/
├── README.md                          ← you are here
├── skills/
│   ├── daily/SKILL.md                 ← /daily
│   ├── log/SKILL.md                   ← /log
│   ├── onboard/SKILL.md               ← /onboard
│   ├── respond/SKILL.md               ← /respond
│   └── sync-project/SKILL.md          ← /sync-project
└── shared/
    ├── project-picker.md              ← select/create project
    ├── read-project-context.md        ← load project data
    ├── log-and-extract.md             ← write entry + action items
    └── route-files.md                 ← classify + route files
```

## License

MIT
