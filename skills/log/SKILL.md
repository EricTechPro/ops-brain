---
name: log
description: Add an entry to a project's conversation log.
---

## Steps

1. **Pick project**

> [!sub-workflow] Project Picker
> Read and execute `shared/project-picker.md`
> Params: allow_new = false

2. **Gather details** — Ask the user:
   - What happened? (meeting, email, call, document shared, update, deliverable)
   - Brief summary of the interaction
   - Any action items that came out of it?

3. **Log entry + extract action items**

> [!sub-workflow] Log and Extract
> Read and execute `shared/log-and-extract.md`
> Input: project-name from step 1, entry-type and summary from step 2

4. **Complete items** — Ask if any existing action items were completed:
   - If yes: move them from `## Action Items` to `## Completed` with `done YYYY-MM-DD`
   - Change `- [ ]` to `- [x]`

5. **Confirm** — Show the updated log entry and any action item changes.
