---
name: log
description: "Log a project interaction to conversation-log.md and extract action items. Smart context: when invoked mid-conversation, infers what happened from the conversation history — no need to re-explain. Also accepts inline args (\"/log acme-corp call with Sarah\"). Use when the user says \"log this\", \"add to the log\", \"record this\", or after any project interaction that should be tracked."
---

**Usage:** `/log` or `/log <project> <what happened>`

## Steps

1. **Pick project**

> [!sub-workflow] Project Picker
> Read and execute `shared/project-picker.md`
> Params: allow_new = false

   If no project was specified and you're mid-conversation, infer the project from context — which project was being discussed? If still unclear, use the picker.

2. **Understand the interaction** — Work from whatever context is available, in this priority order:

   **Mid-conversation (no params):** Scan the current conversation for what just happened — calls made, emails discussed, decisions reached, deliverables mentioned. Infer the entry type and summary. Present: "I'll log this as [type] for [project]: [summary]. Any changes?" Then proceed.

   **Inline args** (e.g., `/log acme-corp call with Sarah about timeline`): Parse directly. Infer type from keywords: "call/spoke/talked" → call, "email/sent/received/wrote" → email-sent or email-received, "shared/sent doc/attached" → doc-shared, "update/status/milestone" → update, "delivered/completed/finished" → deliverable, "received/got" → received.

   **Fallback:** If the conversation has no relevant context and no inline args were given, ask ONE question: "What happened?" Then infer the type and summary from the response. Only ask follow-up questions if genuinely ambiguous.

3. **Log entry + extract action items**

> [!sub-workflow] Log and Extract
> Read and execute `shared/log-and-extract.md`
> Input: project-name from step 1, entry-type and summary from step 2

4. **Complete items** — Ask if any existing action items were completed:
   - If yes: move them from `## Action Items` to `## Completed` with `done YYYY-MM-DD`
   - Change `- [ ]` to `- [x]`

5. **Confirm** — Show the updated log entry and any action item changes.
