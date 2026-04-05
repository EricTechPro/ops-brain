---
name: start
description: "First-run vault setup and health check: verify folder structure, set up Gmail API, personalize team.md, orient on available skills. Safe to re-run as health check. Use when the user says \"get started\", \"set up\", \"first time\", \"how does this work\", or \"run setup\"."
---

**Usage:** `/start`

## Step 0: Pre-check — Dependencies

Before anything else, verify the environment has what it needs. Run all checks silently, then report.

### 0a. Obsidian

Check if `.obsidian/` directory exists in the vault root.

- **If missing:** The vault isn't set up as an Obsidian vault yet. Show:

```
Obsidian not detected (.obsidian/ folder missing).

This vault is designed to work with Obsidian — a free, local-first
note-taking app that gives you a visual interface for your notes.

  1. Download Obsidian: https://obsidian.md
  2. Open Obsidian → "Open folder as vault" → select this folder
  3. Re-run /start

You can still use the CLI skills without Obsidian, but you'll miss
the visual graph, search, and linking features.
```

Ask: "Continue without Obsidian, or set it up first?"
- **Continue** → proceed (skills work fine without it)
- **Set up first** → stop here, let them install and come back

- **If present:** silently pass. No output needed.

### 0b. Obsidian community plugins (optional)

If `.obsidian/` exists, check `.obsidian/community-plugins.json`. This is informational only — don't block on it. If the file is empty or contains `[]`, mention:

```
Tip: Obsidian community plugins can enhance your vault.
Recommended: Dataview, Tasks, Calendar, Templater.
You can install these later from Obsidian → Settings → Community plugins.
```

### 0c. Claude Code plugins

Check that the required Claude Code plugins are installed by running `claude plugin list`.

**Required:**
- `ops-brain` — the core plugin (must be installed since they're running `/start`, but verify)

**Recommended:**
- `obsidian` (from obsidian-skills) — Obsidian-aware markdown, canvas, and bases skills

For any missing recommended plugin, show install commands:

```
Recommended plugin not installed: obsidian

  Install it:
    claude plugin marketplace add github:kepano/obsidian-skills
    claude plugin install obsidian --scope project
```

### 0d. Summary

Show a compact status line:

```
Pre-check:
  Obsidian:       detected ✓ / not found ✗
  Obsidian plugins: N community plugins / none yet
  ops-brain:      installed ✓
  obsidian-skills: installed ✓ / not installed (optional)
```

If all required checks pass, proceed to Step 1. If Obsidian is missing and the user chose to set it up first, stop here.

## Step 1: Welcome Banner + State Detection

Display the welcome banner:

```
  ╔══════════════════════════════════════════════╗
  ║                                              ║
  ║    ◆  Ops Brain — Business Second Brain      ║
  ║       Project Management for Busy Owners     ║
  ║                                              ║
  ╚══════════════════════════════════════════════╝
```

Detect vault state to determine first-run vs re-run:

1. Check if `projects/` contains any project folders
2. Check if `team.md` has entries beyond the default `@eric` row
3. Check if `scripts/.env` exists with `GMAIL_USER_EMAIL` set

**First-run** = zero projects AND team.md has only the default entry → proceed to Step 2.
**Re-run** = any projects exist OR team.md has been customized → jump to **Step 6 (Health Check)**.

## Step 2: Discovery (first-run only)

Ask two questions sequentially. Infer context from the answers — don't ask follow-ups.

**Q1:** "Tell me about your business in a couple sentences — what you do, how many clients or projects you manage, and your role."

From the response, infer:
- `role` — owner, freelancer, consultant, agency lead, etc.
- `business_type` — consulting, agency, freelance, SaaS, etc.
- `project_scale` — rough number of active projects/clients

**Q2:** "What's falling through the cracks right now?" (offer examples: losing track of emails, forgetting follow-ups, no single source of truth, client communication chaos)

From the response, determine `primary_pain` to tailor orientation in Step 7:
- Email chaos → emphasize `/sync-project` + `/respond`
- Task tracking → emphasize `/daily` + action items
- Organization → emphasize `/onboard` + folder structure
- General → balanced orientation

## Step 3: Preview & Confirm

Show the vault structure as a preview. Do NOT create anything yet — wait for confirmation.

```
Here's how your vault is organized:

  projects/[name]/
  ├── overview.md            ← Client profile, contacts, Gmail label
  ├── conversation-log.md    ← Single source of truth (all interactions)
  ├── links.md               ← URL library
  ├── constants/             ← Contracts, invoices, agreements
  ├── responses/             ← Draft emails (temporary, auto-deleted)
  └── shared/deliverables/   ← Quotes, proposals, work product

  Supporting:
  ├── inbox/                 ← Drop anything here to process later
  ├── daily/                 ← Morning briefings
  ├── templates/             ← 9 reusable templates
  ├── archives/              ← Completed projects
  ├── scripts/               ← Gmail sync engine
  └── team.md                ← Your team directory

Everything flows through conversation-log.md per project.
Action items are auto-extracted and tracked. /daily surfaces them all.
```

After showing the preview, verify all required directories exist. Create any that are missing:
- `inbox/`, `daily/`, `projects/`, `templates/`, `archives/`, `scripts/`

Report results:
- If all present: "All vault folders present ✓"
- If any created: "Created: inbox/, archives/" (list what was created)

### Deploy Gmail sync script

The Gmail sync script ships with the ops-brain plugin. Deploy it to the vault if not already present:

1. Check if `scripts/gmail_sync.py` exists in the vault
2. If missing, copy it from the plugin's `scripts/` directory (relative to this skill: `../../scripts/gmail_sync.py`) into the vault's `scripts/gmail_sync.py`
3. Do the same for `scripts/requirements.txt` and `scripts/.env.example`
4. Report: "Gmail sync script: deployed ✓" or "Gmail sync script: already present ✓"

> **Important:** Never copy `.env`, `.gmail-credentials/`, or `__pycache__/` — these contain user-specific secrets and are created during Gmail setup (Step 4).

Check templates exist in `templates/`:
- `conversation-log.md`, `project-overview.md`, `link-library.md`
- If any missing: warn (do not create — templates are hand-crafted)

Check `CLAUDE.md` exists. If missing: warn "CLAUDE.md is missing — restore from git with `git checkout CLAUDE.md`"

## Step 4: Gmail API Setup

This is the critical prerequisite. `/sync-project` and `/onboard` Gmail imports depend on it.

### 4a. Auto-detect Gmail readiness

Run these checks silently, then report:

1. `scripts/.env` exists and contains `GMAIL_USER_EMAIL`?
2. `scripts/.gmail-credentials/credentials.json` exists?
3. `scripts/.gmail-credentials/token.json` exists?
4. Python google packages installed? Run: `python3 -c "from google.oauth2.credentials import Credentials" 2>&1`

If ALL pass → report "Gmail: ready ✓" and skip to Step 5.

### 4b. If Python packages missing

```
Install required packages:
  pip install google-auth google-auth-oauthlib google-api-python-client
```

### 4c. If credentials or .env missing — show setup guide

```
Gmail API Setup (~5 min, one-time):

  Step 1 — Create a Google Cloud project
    1. Go to console.cloud.google.com
    2. Click the project dropdown (top-left, next to "Google Cloud")
    3. Click "New Project"
    4. Name it anything (e.g. "Ops Brain") → Create
    5. Make sure your new project is selected in the dropdown

  Step 2 — Enable the Gmail API
    1. In the search bar at the top, type "Gmail API"
    2. Click "Gmail API" in the results
    3. Click "Enable"

  Step 3 — Configure OAuth consent screen
    1. Go to APIs & Services → OAuth consent screen (left sidebar)
    2. Select "External" → Create
    3. Fill in only the required fields:
       - App name: Ops Brain
       - User support email: your email
       - Developer contact email: your email
    4. Click "Save and Continue" through the remaining steps
    5. Click "Back to Dashboard"

  Step 4 — Create OAuth credentials
    1. Go to APIs & Services → Credentials (left sidebar)
    2. Click "+ Create Credentials → OAuth client ID"
    3. Application type: Desktop app
    4. Name: Ops Brain (or anything)
    5. Click "Create"
    6. Click "Download JSON" on the confirmation dialog
    7. Save the file to:
       scripts/.gmail-credentials/credentials.json

  Step 5 — Configure your environment
    Create scripts/.env (or copy scripts/.env.example):

      GMAIL_USER_EMAIL=you@yourdomain.com
      GMAIL_CREDENTIALS_FILE=scripts/.gmail-credentials/credentials.json
      GMAIL_TOKEN_FILE=scripts/.gmail-credentials/token.json
      GMAIL_DOWNLOAD_DIR=/tmp/gmail-sync

  Step 6 — Install Python dependencies
    pip3 install -r scripts/requirements.txt

  Step 7 — Authenticate (opens browser once)
    python3 scripts/gmail_sync.py label "INBOX" --max-results 1

    Your browser opens → sign in → click Allow.
    token.json is saved automatically. One-time only.

  🔒 scripts/.env and credentials are in .gitignore
     — they never leave your machine.
```

Ask: "Have you completed Gmail setup, want help walking through it now, or skip for later?"

- **Done** → verify by running `python3 scripts/gmail_sync.py label "INBOX" --max-results 1`
- **Help** → walk through each step interactively, creating `.env` and `.gmail-credentials/` as needed
- **Skip** → note Gmail is not configured, continue (can re-run `/start` later)

### 4d. Gmail label organization tip

Always show this, whether Gmail is set up or not:

```
Tip — Organize your projects as Gmail labels:

  In Gmail → Settings → Labels → Create:
    Projects/Acme Corp
    Projects/Big Client
    Projects/Side Gig

  Then add filters to auto-label incoming mail.

  When you /onboard a project, reference the label name
  to pull all emails into your vault automatically.
```

## Step 5: Personalization

### 5a. Team setup

Read current `team.md` and display the existing entries. Confirm the owner entry is correct.

Ask: "Anyone else to add? Team members, VAs, contractors — I need a handle, name, and role for each. Or 'skip'."

For each person, collect handle, name, and role. Add to `team.md`.

### 5b. First project prompt

Ask: "Ready to onboard your first project? I can import from Gmail, local files, or you can just start with a name."

- If yes → suggest the user run `/onboard`
- If no → continue to Step 7 (orientation)

## Step 6: Health Check (re-run mode)

Display health check banner:

```
  ╔══════════════════════════════════════════════╗
  ║    ◆  Ops Brain — Vault Health Check         ║
  ╚══════════════════════════════════════════════╝
```

Run all prerequisite checks from Steps 3-4. Additionally:

- Count project folders in `projects/` (active) and `archives/` (archived)
- Count entries in `team.md`
- Count files in `inbox/`
- Find the most recent file in `daily/` to determine last briefing date
- Check Gmail config (same as Step 4a)
- Check Python deps (same as Step 4a)

Report:

```
  Projects:     N active, M archived
  Team:         N members
  Gmail:        configured ✓ / needs setup ✗
  Python deps:  installed ✓ / missing ✗
  Inbox:        N items waiting
  Last daily:   YYYY-MM-DD (or "none yet")
  Templates:    N found
```

If any issues found (missing templates, broken Gmail, items piling up in inbox), suggest specific fixes.

Then proceed to Step 7 (orientation — useful as a refresher even on re-run).

## Step 7: Orientation

Tailor the emphasis based on `primary_pain` from Q2 (first-run) or show balanced view (re-run).

```
Available commands:

  /start          You are here — setup & health check
  /onboard        Add a new project (Gmail, files, or from scratch)
  /sync-project   Pull new emails from Gmail into a project
  /daily          Morning dashboard: tasks, activity, stale warnings
  /log            Record a call, meeting, or update
  /respond        Draft email as copyable HTML for Gmail

  Workflow:
  ┌─────────┐    ┌──────────────┐    ┌──────┐    ┌─────────┐
  │ /onboard │ →  │ /sync-project │ →  │ /log │ →  │ /respond │
  └─────────┘    └──────────────┘    └──────┘    └─────────┘
                         ↓
                    ┌─────────┐
                    │  /daily  │  ← run every morning
                    └─────────┘
```

If `primary_pain` was identified, add a tailored callout:
- Email chaos: "Start with `/onboard` to import your Gmail, then `/sync-project` keeps it current."
- Task tracking: "Use `/daily` each morning — it surfaces all pending tasks across projects."
- Organization: "Run `/onboard` for each project. Everything lands in conversation-log.md automatically."

## Step 8: Next Actions Menu

Offer via conversation:

1. **Onboard first project** → suggest `/onboard`
2. **Set up Gmail** (if skipped earlier) → re-run Step 4
3. **Run morning dashboard** → suggest `/daily`
4. **Done for now** → exit with: "Run `/daily` tomorrow morning to start your day."
