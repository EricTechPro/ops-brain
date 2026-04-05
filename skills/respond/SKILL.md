---
name: respond
description: "Draft an email response as browser-openable HTML with one-click copy for Gmail. Reads project context, conversation history, and contact preferences to match tone. Auto-applies business cooperation style for partnership/sales/sponsorship threads. Use when the user says \"reply to\", \"draft a response\", \"write an email to\", \"respond to this email\", or \"help me answer this\"."
---

## Steps

1. **Pick project**

> [!sub-workflow] Project Picker
> Read and execute `shared/project-picker.md`
> Params: allow_new = false

2. **Understand the request** — If the user provided context inline (e.g., `/respond acme-corp reply to Sarah's pricing question — confirm $5k/month`), parse it and only ask for what's missing. Otherwise ask:
   - What are you responding to? (paste the email or describe it)
   - Key points to include in the response
   - Tone: professional / friendly / firm / casual

3. **Read project context**

> [!sub-workflow] Read Project Context
> Read and execute `shared/read-project-context.md`
> Input: project-name from step 1

   Use contacts, communication prefs, and recent entries to inform the draft.

   If the email being replied to is part of an ongoing thread, search conversation-log.md for matching `thread:<id>` or subject line entries. Use the thread history to maintain continuity — reference previous commitments, follow up on open questions, and avoid repeating information already exchanged.

4. **Load style guide** — This detection happens automatically — no need to ask the user. If the project overview mentions partnerships, sales, or sponsorship in its scope, or if the email content involves pricing, proposals, or collaboration terms:
   - Read `templates/business-cooperation-style.md`
   - Identify the conversation stage (initial contact / discovery / proposal / objection handling / closing / follow-up)
   - Apply the style directives when drafting — use Eric's proven patterns as the foundation

5. **Create response file** — Generate a single standalone HTML file at `projects/[name]/responses/YYYY-MM-DD-topic.html` using this structure:

   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
     <meta charset="UTF-8">
     <title>Response: {{subject}}</title>
     <style>
       body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 700px; margin: 40px auto; padding: 20px; color: #333; }
       .meta { color: #666; font-size: 14px; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
       .email-body { font-size: 15px; line-height: 1.6; }
       .copy-btn { position: fixed; top: 20px; right: 20px; background: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-size: 14px; }
       .copy-btn:hover { background: #45a049; }
       .copy-btn.copied { background: #888; }
     </style>
   </head>
   <body>
     <button class="copy-btn" onclick="copyEmail()">Copy to clipboard</button>
     <div class="meta">
       <strong>To:</strong> {{recipient}}<br>
       <strong>Subject:</strong> {{subject}}<br>
       <strong>Date:</strong> {{date}}
     </div>
     <div id="email-body" class="email-body">
       <!-- Email body here using ONLY: <p>, <b>, <br>, <ul>, <ol>, <li> -->
       <!-- No inline CSS, no <style> blocks in the body -->
     </div>
     <script>
       async function copyEmail() {
         const body = document.getElementById('email-body');
         const sel = window.getSelection();
         const range = document.createRange();
         range.selectNodeContents(body);
         sel.removeAllRanges();
         sel.addRange(range);
         try {
           await navigator.clipboard.write([
             new ClipboardItem({
               'text/html': new Blob([body.innerHTML], { type: 'text/html' }),
               'text/plain': new Blob([body.innerText], { type: 'text/plain' })
             })
           ]);
         } catch {
           document.execCommand('copy');
         }
         sel.removeAllRanges();
         const btn = document.querySelector('.copy-btn');
         btn.textContent = 'Copied!';
         btn.classList.add('copied');
         setTimeout(() => { btn.textContent = 'Copy to clipboard'; btn.classList.remove('copied'); }, 2000);
       }
     </script>
   </body>
   </html>
   ```

   - Write the email body inside `<div id="email-body">` using only semantic HTML: `<p>`, `<b>`, `<br>`, `<ul>`, `<ol>`, `<li>`
   - No inline CSS in the email body — Gmail strips it anyway
   - The `.meta` section (To/Subject/Date) is for reference only and is NOT copied
   - Add internal strategy notes as an HTML comment `<!-- ... -->` (not visible, not copied)
   - After creating the file, open it in the browser with `open` command

6. **Present and open** — Show the email text in the conversation for review. After approval, open the HTML file in the default browser. Eric clicks "Copy to clipboard" → pastes into Gmail compose.

7. **After sending** — Ask: "Have you sent it?"
   - If yes:

> [!sub-workflow] Log and Extract
> Read and execute `shared/log-and-extract.md`
> Input: project-name, entry-type = email-sent, summary of what was sent

     Then delete the response file from `responses/`.
   - If not yet: leave the file for later. Remind to run `/log` after sending.
