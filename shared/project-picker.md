# Project Picker

Identify which project the user wants to work with.

## Params
- `allow_new` — if true, accept "new <name>" to create a new project (default: false)

## Steps

1. **Check if project was provided as argument** — if the user already specified a project name (e.g., `/log acme-corp`), skip to step 3.

2. **Present options** — Scan `projects/` for folder names.
   - If `projects/` is empty (no folders): if `allow_new = true`, prompt to create one. If `allow_new = false`, tell the user there are no active projects and suggest running `/onboard` first.
   - Otherwise, present as a numbered list:
   ```
   Which project?
   1. acme-corp
   2. greenfield-app
   3. smith-consulting
   ```
   If `allow_new = true`, also show: `Or say "new <name>" to create a new project.`

3. **Resolve** — Match the user's input against folder names:
   - Exact match → use it
   - Partial match (one result) → confirm: "Did you mean `acme-corp`?"
   - Partial match (multiple) → show matches, ask to pick
   - No match in `projects/` → also check `archives/`. If found there: "Found `<name>` in archives/. Would you like to re-activate it (move back to projects/) or work on it in place?"
   - No match anywhere + `allow_new = false` → "No project found. Available: [list]"
   - No match anywhere + `allow_new = true` → treat as new project

4. **If new project** (only when `allow_new = true`):
   - Convert name to kebab-case, confirm folder name with user
   - Create folder structure under `projects/<project-name>/`:
     ```
     projects/<project-name>/
     ├── overview.md            ← from templates/project-overview.md
     ├── conversation-log.md    ← from templates/conversation-log.md
     ├── links.md               ← from templates/link-library.md
     ├── constants/
     ├── responses/
     └── shared/
         └── deliverables/
     ```
   - Copy each template, replace `{{Project Name}}` with the actual name, `{{date}}` with today's date
   - Create empty directories

5. **Return** — the confirmed `<project-name>` (kebab-case folder name)
