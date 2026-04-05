# ops-brain

A Claude Code plugin for project managers handling multiple projects. Provides 5 skills for daily briefings, conversation logging, email responses, Gmail sync, and project onboarding — all backed by an Obsidian vault as your second brain.

## Installation

```bash
claude plugin marketplace add github:EricTechPro/ops-brain
claude plugin install ops-brain
```

## Skills

| Skill | Command | What it does |
|-------|---------|-------------|
| Daily | `/daily` | Morning briefing — scans all projects for pending tasks, recent activity, and inbox status (read-only) |
| Log | `/log` | Adds a timestamped entry to a project's conversation log and extracts action items |
| Respond | `/respond` | Crafts an email response as rich HTML, opens in browser for Gmail copy-paste, then logs and deletes |
| Onboard | `/onboard` | Sets up new or existing projects — imports from Gmail/files/pasted text, builds profile, generates key events report |
| Sync Project | `/sync-project` | Fetches project emails from a Gmail label, deduplicates, groups by thread, and routes attachments |

## Required Vault Structure

Your Obsidian vault needs this folder layout:

```
inbox/              <- Unprocessed dumps (PDFs, text, CSVs, links, screenshots)
daily/              <- Dated notes and briefings
projects/[name]/    <- Per-project folders (see below)
templates/          <- Reusable note templates
archives/           <- Completed projects
scripts/            <- gmail_sync.py for Gmail integration
team.md             <- Global handle -> name -> role lookup
```

Each project folder:

```
projects/[project-name]/
├── overview.md            <- Project + client profile, contacts, communication prefs
├── conversation-log.md    <- Source of truth — all interactions
├── links.md               <- Categorized URL library
├── constants/             <- Contracts, agreements, invoices, NDAs
├── responses/             <- Temporary email responses (deleted after sent)
└── shared/
    └── deliverables/      <- Quotes, proposals, work product
```

## Shared Sub-workflows

Skills share internal modules in `shared/` for common operations:

- **project-picker.md** — Scan projects, present options, resolve selection (with "new project" variant)
- **read-project-context.md** — Load overview, contacts, recent log entries, pending actions
- **log-and-extract.md** — Write formatted log entry + extract action items in one step
- **route-files.md** — Classify and route files by type (contracts, CSVs, images, etc.)

These are internal building blocks — not user-invokable.

## Gmail Integration

Requires `scripts/gmail_sync.py` with OAuth2 (read-only). Used by `/sync-project` and `/onboard` for email import. See the vault's `scripts/` directory for setup.

## License

MIT
