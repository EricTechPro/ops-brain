---
name: start
description: "First-run vault setup and health check. Scans vault, auto-creates structure, deploys scripts, reports status. Zero questions — fully autonomous. Safe to re-run. Use when the user says \"get started\", \"set up\", \"first time\", \"how does this work\", or \"run setup\"."
---

**Usage:** `/start`

This skill runs autonomously with **zero user questions**. It scans, acts, and reports in one pass.

---

## Phase 1: Silent Scan

Run ALL checks silently. Collect results — do not output anything to the user yet.

### 1a. Git identity
- Run `git config user.name` → `git_name`
- Run `git config user.email` → `git_email`

### 1b. Vault folders
- Check existence of each: `inbox/`, `daily/`, `projects/`, `templates/`, `archives/`, `scripts/`
- Store: `folders_present`, `folders_missing`

### 1c. Obsidian
- Check `.obsidian/` exists → `obsidian_detected`
- If exists, read `.obsidian/community-plugins.json` → `plugin_count`

### 1d. team.md
- Check if `team.md` exists
- If exists, read it. Count entries → `team_count`
- Check if customized beyond default → `team_customized`

### 1e. Projects
- List subdirectories in `projects/` → `active_projects` (names + count)
- List subdirectories in `archives/` → `archived_projects` (count)

### 1f. Templates
- Check `templates/` for 3 required: `conversation-log.md`, `project-overview.md`, `link-library.md`
- Store: `templates_present`, `templates_missing`

### 1g. CLAUDE.md
- Check if `CLAUDE.md` exists at vault root → `claude_md_exists`

### 1h. Scripts
- Check if `scripts/gmail_sync.py` exists in vault
- Check if `scripts/requirements.txt` exists in vault
- Check if `scripts/.env.example` exists in vault

### 1i. Gmail readiness (4 checks)
1. `scripts/.env` exists AND contains `GMAIL_USER_EMAIL` with a real value (not placeholder)
2. `scripts/.gmail-credentials/credentials.json` exists
3. `scripts/.gmail-credentials/token.json` exists
4. Python deps installed: `python3 -c "from google.oauth2.credentials import Credentials" 2>&1`
- `gmail_ready` = all 4 pass

### 1j. Daily notes
- Find most recent file in `daily/` → `last_daily` (date or "none")

### 1k. Inbox
- Count files in `inbox/` → `inbox_count`

### 1l. Mode detection
- `first_run` = `active_projects` is empty AND `team_customized` is false
- Otherwise `re_run` = true

---

## Phase 2: Silent Act

Do all of this without asking. No previews. No confirmations.

### 2a. Create missing vault directories
- For each folder in `folders_missing`: create it
- Track what was created → `folders_created`

### 2b. Deploy scripts from plugin
- If `scripts/gmail_sync.py` missing in vault: copy from plugin's `scripts/` directory (relative to this skill: `../../scripts/gmail_sync.py`)
- Same for `scripts/requirements.txt` and `scripts/.env.example`
- **Never copy** `.env`, `.gmail-credentials/`, or `__pycache__/` — these are user secrets
- Track what was deployed → `scripts_deployed`

### 2c. Auto-populate team.md (first-run only)
- If `team.md` does not exist OR has only the default entry:
  - Use `git_name` and `git_email` to set the owner row
  - Create or update `team.md` with the detected identity
- If `team.md` already has custom entries: do not touch it

---

## Phase 3: Report

Output everything in one consolidated block.

### 3a. Banner

First-run:
```
  ╔══════════════════════════════════════════════╗
  ║    ◆  Ops Brain — Setup Complete             ║
  ╚══════════════════════════════════════════════╝
```

Re-run:
```
  ╔══════════════════════════════════════════════╗
  ║    ◆  Ops Brain — Health Check               ║
  ╚══════════════════════════════════════════════╝
```

### 3b. Identity (first-run only)
```
  Owner:  {git_name} <{git_email}>  (from git config)
```

### 3c. Status table

```
  Vault Structure
  ────────────────────────────────────────
  Folders:      all present ✓  /  created: {list}
  Templates:    3/3 found ✓  /  missing: {list} ✗
  CLAUDE.md:    present ✓  /  missing ✗
  Scripts:      deployed ✓  /  already present ✓
  Obsidian:     detected ({plugin_count} plugins)  /  not found

  Projects
  ────────────────────────────────────────
  Active:       {count} ({names if ≤ 5})
  Archived:     {count}
  Team:         {count} members
  Inbox:        {count} items
  Last daily:   {date}  /  none yet

  Gmail
  ────────────────────────────────────────
  .env config:  ✓ / ✗
  Credentials:  ✓ / ✗
  Token:        ✓ / ✗
  Python deps:  ✓ / ✗
  Status:       ready ✓  /  needs setup ↓
```

### 3d. Warnings (only show sections with issues)

If templates missing:
```
Missing templates — restore from git:
  git checkout templates/conversation-log.md templates/project-overview.md
```

If CLAUDE.md missing:
```
CLAUDE.md missing — restore from git:
  git checkout CLAUDE.md
```

If Obsidian not detected:
```
Obsidian not found — optional but recommended:
  Download from https://obsidian.md → "Open folder as vault" → select this folder
```

If inbox has items (re-run):
```
Inbox has {count} items — process with /onboard or move to a project folder.
```

### 3e. Gmail setup guide (only if gmail_ready is false)

```
Gmail API Setup (~5 min, one-time):

  1. Create a Google Cloud project
     → console.cloud.google.com → project dropdown (top-left)
     → "New Project" → name it "Ops Brain" → Create
     → Make sure it's selected in the dropdown

  2. Enable Gmail API
     → Search bar: type "Gmail API" → click result → Enable

  3. OAuth consent screen
     → Left sidebar: APIs & Services → OAuth consent screen
     → Select "External" → Create
     → App name: Ops Brain, emails: yours
     → "Save and Continue" through all steps → "Back to Dashboard"

  4. Create credentials
     → Left sidebar: APIs & Services → Credentials
     → "+ Create Credentials" → "OAuth client ID"
     → Type: Desktop app → Name: Ops Brain → Create
     → "Download JSON" → save to:
       scripts/.gmail-credentials/credentials.json

  5. Configure environment
     → Copy scripts/.env.example to scripts/.env
     → Set GMAIL_USER_EMAIL to your email address

  6. Install Python dependencies
     → pip3 install -r scripts/requirements.txt

  7. Authenticate (opens browser once)
     → python3 scripts/gmail_sync.py label "INBOX" --max-results 1
     → Browser opens → sign in → Allow
     → token.json saved automatically (one-time)

  Tip: Create Gmail labels for your projects:
    Gmail → Settings → Labels → "Projects/Client Name"
    Add filters to auto-label incoming mail.

  Re-run /start after setup to verify ✓
```

### 3f. Orientation

```
Available commands:

  /onboard        Add a new project (Gmail, files, or from scratch)
  /sync-project   Pull new emails from Gmail into a project
  /daily          Morning dashboard: tasks, activity, stale warnings
  /log            Record a call, meeting, or update
  /respond        Draft email as copyable HTML for Gmail

  Workflow:
  ┌──────────┐    ┌───────────────┐    ┌──────┐    ┌─────────┐
  │ /onboard │ →  │ /sync-project │ →  │ /log │ →  │ /respond │
  └──────────┘    └───────────────┘    └──────┘    └─────────┘
                         ↓
                    ┌─────────┐
                    │  /daily  │  ← run every morning
                    └─────────┘
```

### 3g. Next step (one line, no menu)

- First-run + Gmail ready: `Ready to go. Run /onboard to set up your first project.`
- First-run + Gmail not ready: `Run /onboard to start a project. Gmail import available after setup above.`
- Re-run + issues found: `Fix the items marked ✗ above, then re-run /start to verify.`
- Re-run + all healthy: `Everything looks good. Run /daily for your morning dashboard.`
