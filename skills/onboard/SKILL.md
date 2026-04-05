---
name: onboard
description: "Set up a new project or bulk-import data into an existing one from Gmail labels, local files, or pasted text. Creates folder structure, auto-extracts client profile and contacts, generates a key events timeline. Use for \"new project\", \"set up a project\", \"import project data\", \"add a new client\", or \"re-import data for <project>\"."
---

**Usage:** `/onboard` or `/onboard <project-name>`

## Step 1: Identify Project

> [!sub-workflow] Project Picker
> Read and execute `shared/project-picker.md`
> Params: allow_new = true

## Step 2: Collect Data Sources

Ask all three sequentially. User responds with the value or "none" to skip.

**Q2a — Gmail:** "Do you have a Gmail label for this project? Paste the label name or ID (or 'none'):"

**Q2b — Local files:** "Any local files or folders to import? Paste path(s), one per line (or 'none'):"

**Q2c — Pasted text:** "Any text to paste? Can be emails, notes, URLs, or images with text (or 'none'):"

## Step 3: Fetch & Process All Sources

Process paths A, B, and C in parallel when multiple sources are provided.

### Path A — Gmail Import
- Set up `## Gmail Sync` in overview.md with the label name
- Execute the same Gmail fetch → log → route pipeline from `/sync-project` steps 2-7, with these onboarding adjustments: skip deduplication for new projects (log is empty), create `## Gmail Sync` section fresh
- If `gmail_sync.py` fails (script not found, OAuth expired, network error, no results for label): auto-retry once. If it fails again, report the specific error in plain language and offer: (a) fix the issue and retry, (b) skip Gmail and continue with other sources, (c) paste email text directly (fall through to Path C)
- If any required template is missing from `templates/`, create the file with minimal valid structure (frontmatter + section headings) and note which template was missing so it can be restored later

### Path B — Local File Import

For each path provided, recurse into directories. Detect type and route:

> [!sub-workflow] Route Files
> Read and execute `shared/route-files.md`
> Input: project-name, files = all discovered files from the provided paths

### Path C — Pasted Text
- If images: read the image content, extract text
- Detect type using same heuristics as `shared/route-files.md`
- Route accordingly
- Loop: "More text to paste, or done?"

## Step 4: Conflict Check

Batch ALL issues into one confirmation before writing:

1. **Data contradictions** — sources disagree (e.g., same file from Gmail + local with different versions, contact name mismatches). Suggest which to keep or how to rename.
2. **Duplicates** (existing projects only) — imported data overlaps with what's already in the vault.
3. **Ambiguous routing** — files that don't clearly belong anywhere.

Present all together: "I found N items that need your input:" then list them.

For new projects, skip duplicate checking. If no conflicts → skip entirely.

## Step 5: Auto-Extract Profile (new projects only)

From the data already processed in Step 3, extract:
- Client name, contacts (name, email, phone) → overview.md contacts table
- Industry, website → overview.md client info
- Project scope/description → overview.md project info
- Contract type, pricing → overview.md
- Communication patterns (timezone, channel) → overview.md

Present: "I extracted these details from your data — confirm or correct:"
Only ask user to fill fields that couldn't be auto-detected.

Add initial log entry using `shared/log-and-extract.md` with type = update, summary = "Project onboarded — folder structure created."

For existing projects → skip this step.

## Step 6: Key Events Report

```markdown
## Onboarding Report: {{Project Name}}

### Key Events
- **Started**: YYYY-MM-DD (earliest activity found)
- **Contract**: Type + pricing (if found)
- **Current Status**: Where things stand

### Timeline
- YYYY-MM-DD — First contact / earliest event
- YYYY-MM-DD — Key milestone (contract signed, kickoff, etc.)
- YYYY-MM-DD — Most recent activity

### What's Next
- [ ] @handle — Action item
- [ ] @handle — Next step

### Imported
- N emails (M threads) · N files · N links · N action items
```

Focus on what matters — key events, status, pricing, what's next. User reads it and confirms "this matches what I know."

## Step 7: Next Actions Menu

Offer via AskUserQuestion:
1. **Import more data** — another Gmail label, more files, paste text (→ loop back to Step 2)
2. **Draft an email** — triggers `/respond`
3. **Set up recurring sync** — confirms `/sync-project` is ready
4. **Done for now**
