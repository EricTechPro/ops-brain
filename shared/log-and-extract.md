# Log Entry + Extract Action Items

Write a formatted entry to a project's conversation log and extract any action items. These two steps always happen together — every log entry gets scanned for tasks.

## Input
- `<project-name>` — the project folder name
- `<entry-type>` — one of: email-sent, email-received, call, doc-shared, quote-sent, received, update, deliverable
- `<summary>` — what happened (one line)
- `<details>` — optional additional context
- `<thread>` — optional, for email sync: `{subject, thread_id}` to group under a thread heading

## Steps

### 1. Open conversation log
Open `projects/<project-name>/conversation-log.md`. If it doesn't exist, create it from `templates/conversation-log.md` (replace `{{date}}` with today, `{{Project Name}}` with the project name). If the template is also missing, create a minimal file with frontmatter and these sections: `## Action Items`, `## Log`, `## Completed`.

### 2. Find or create headings
- Find the current month heading `### YYYY-MM`. If missing, create it in chronological order.
- Under that month, find today's date heading `#### YYYY-MM-DD`. If missing, create it.

### 3. Format the entry
Map entry type to emoji and format:

| Type | Emoji | Format |
|------|-------|--------|
| email-sent | 📧 | `- 📧 **Email sent**: Topic — Summary` |
| email-received | 📧 | `- 📧 **Email received**: Sender — Summary` |
| call | 📞 | `- 📞 **Call**: Topic — Key outcome` |
| doc-shared | 📄 | `- 📄 **Doc shared**: Description → [[shared/deliverables/filename]]` |
| quote-sent | 📝 | `- 📝 **Quote sent**: Description → [[shared/deliverables/filename]]` |
| received | 📥 | `- 📥 **Received**: What — Summary` |
| update | 🔄 | `- 🔄 **Update**: Status change or milestone` |
| deliverable | ✅ | `- ✅ **Deliverable**: Work completed and delivered` |

### 4. Thread grouping (email sync variant)
If `<thread>` is provided (used by /sync-project):
- Under the date heading, find or create: `##### 🧵 <subject> \`thread:<thread_id>\``
- Add the entry under the thread heading instead of directly under the date

### 5. Write the entry
Add the formatted entry under today's date (or thread heading). Within a date heading, non-threaded entries go newest-at-top. Threaded entries (under `##### 🧵` headings) are chronological within each thread — thread context reads top-to-bottom.

If a deliverable or document is referenced, add a wikilink: `→ [[shared/deliverables/filename]]`

### 6. Extract action items
Scan the entry content (summary + details) for:
- Explicit tasks, deadlines, or commitments
- Promises made ("I'll send...", "we'll deliver by...")
- Requests received ("can you...", "please send...")

For each action item found:
- Assign `@eric` for Eric's tasks, `@contact` for the project contact's tasks (named in overview.md)
- Ask for due date if not mentioned, or infer from context
- Format: `- [ ] @handle Task description — due YYYY-MM-DD`
- Add to the `## Action Items` section in conversation-log.md
