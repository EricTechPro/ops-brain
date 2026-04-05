# Route Files by Type

Classify and route files to their correct location within a project folder.

## Input
- `<project-name>` — the project folder name
- `<files>` — list of file paths or attachments to route

## Routing Table

For each file, detect its type and route accordingly:

| Pattern | Route | Action |
|---------|-------|--------|
| PDFs with contract/agreement/NDA/SOW/terms/policy keywords (in filename or content) | `projects/<name>/constants/` | Move file + create `-summary.md` using `templates/document-summary.md` |
| Other PDFs | `projects/<name>/` root or conversation-log | Summarize content to markdown |
| Text with email headers (From:/To:/Subject:) | conversation-log | Parse → use `shared/log-and-extract.md` with type email-received |
| Raw text / meeting notes | conversation-log | Parse → use `shared/log-and-extract.md` with type call or update |
| Financial CSVs (columns: amount, invoice, payment, total) | `projects/<name>/constants/` | Convert to markdown table |
| Project tracking CSVs (columns: task, status, deadline, assignee) | conversation-log | Convert rows to action items in `## Action Items` |
| Contact CSVs (columns: name, email, phone, company) | `projects/<name>/overview.md` | Update contacts table |
| URLs / bookmark files / .url / .webloc | `projects/<name>/links.md` | Categorize under appropriate heading |
| Images (.png, .jpg, .gif, .webp) | `projects/<name>/constants/` | Move + create reference note |
| Deliverables (proposals, quotes, work product) | `projects/<name>/shared/deliverables/` | Move + add `[[wikilink]]` in conversation-log |
| Unknown / ambiguous | — | Collect and present to user for manual routing |

## Detection Heuristics

**Contract detection** — match if filename OR first-page content contains any of:
`contract`, `agreement`, `nda`, `non-disclosure`, `sow`, `statement of work`, `terms`, `policy`, `invoice`, `receipt`

**CSV type detection** — check column headers (first row):
- Financial: any of `amount`, `total`, `invoice`, `payment`, `price`, `cost`, `revenue`
- Project tracking: any of `task`, `status`, `deadline`, `assignee`, `priority`, `due`
- Contact: any of `name`, `email`, `phone`, `company`, `role`, `title`

**Deliverable detection** — match if filename contains: `proposal`, `quote`, `estimate`, `deliverable`, `report`, `presentation`

## Steps

1. For each file in `<files>`:
   - Detect type using the heuristics above
   - Before writing to the destination, check if a file with the same name already exists there. If it does: (a) if the contents are identical, skip it and note "duplicate skipped"; (b) if contents differ, append a timestamp suffix (`-YYYYMMDD-HHMM`) before the extension and note both versions to the user.
   - Route to the correct destination
   - Perform the associated action (move, summarize, parse, etc.)
   - Track what was routed where

2. Collect any files that don't clearly match a pattern → present to user:
   ```
   I couldn't auto-route these files:
   - mystery-doc.pdf — Where should this go?
   - notes.txt — Is this meeting notes or something else?
   ```

3. Report summary:
   ```
   Routed N files:
   - N → constants/
   - N → links.md
   - N → shared/deliverables/
   - N → conversation-log (as entries)
   - N → needs your input
   ```
