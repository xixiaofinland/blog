# Blog Project Instructions

## Style

- No em dashes (—). Use commas, colons, or periods instead.
- Write punchy, scannable sentences. Short paragraphs.
- Avoid AI-heavy phrasing. Sound human.
- Use bold for emphasis sparingly.
- Headings: H1 for title, H2 for sections, H3 for subsections.
- Use concrete examples over abstract concepts.
- End with a clear takeaway or call to reflection.

### Writing Pattern (Kent Beck / _Tidy First?_ style)

Model all blog posts after this pattern:

**Sentence rhythm:** Short declarative sentence. Then a fragment. Then a question? Vary length deliberately. Long setup, then one-line punch. Ratio: roughly 2-3 short sentences per 1 long setup. All-short = staccato drift, loses Beck contrast. Fix: insert one longer sentence before a run of short punches.

**Voice:** Direct second person. "You see this." "You've been there." Drop reader into the scene before explaining anything.

**Hand-holding moves:**

- Narrate the reader's experience as it happens: "You read the section and wonder..."
- Anticipate the objection, answer it immediately (parenthetical or next sentence)
- Concrete scenario first, abstract principle second — earn the theory

**Structure per section:**

1. Name the concrete problem the reader recognizes
2. Show it (example, image, diagram)
3. Fix/reframe it
4. Explain _why_ in 1-2 sentences
5. One-sentence landing that closes the point

**Key moves:**

- Short sentence after a long one for emphasis
- Rhetorical question followed immediately by the answer
- Parenthetical asides for objections, so main flow stays clean
- One-sentence paragraph endings to signal "done, move on"
- Never re-explain what the reader just read

## Content

- LinkedIn articles: 1000-2500 words, conversational but professional.
- Match the existing tone in other posts.

## Workflow

- When expanding content, ask which section to work on first.
- Don't rewrite large sections without approval.
- Save new drafts as `.md` files in `src/`.
- Update `SUMMARY.md` when adding new posts.

## mdBook Navigation

The blog uses a latest-first structure for AI content in `src/SUMMARY.md`.

Preferred workflow:

- When an agent is preparing a commit that adds or updates AI threads, it should check whether the AI section in `src/SUMMARY.md` still matches the intended structure.
- The preferred AI order is: `Latest` first, then yearly archive pages.
- Minor drift is acceptable. If the navigation is slightly out of date, fix it when noticed instead of treating it as a blocking error.
- Prefer using `python3 scripts/refresh_ai_navigation.py` to refresh the AI section instead of hand-editing that block.
- When adding a new AI thread and you want it in the latest list immediately, use `python3 scripts/refresh_ai_navigation.py --add src/<file>.md`.

## Editing Collaboration

When proposing prose changes:

1. Show a diff view (before/after lines). Do not apply.
2. Wait for the user to say "go" or "update" before applying any change.
3. If the user continues without saying either, treat it as "no update" — do not apply.
4. The user may cherry-pick manually from the diff — do not re-apply what they skipped.
5. Keep each diff small and isolated so individual lines are easy to accept or ignore.

## Article Creation Workflow

When starting a new article, proactively suggest this process:

**1. Brief first.**
Create a `src/<article-name>-brief.md` with: topic, target audience, key argument, and a bullet list of sections. Align on structure before writing any prose.

**2. Outline before prose.**
Turn the brief into a skeleton with section headings and one-line summaries. Restructure bullets, not paragraphs.

**3. Raw thoughts → draft.**
User drops rough ideas or voice-memo notes. Agent extracts structure and drafts. User corrects direction, adjusts one word at a time.

**4. Article template.**
Default structure for technical articles:

- Hook (concrete observation, what's changing)
- Analogy (A→B, not A→A+)
- Challenge (name the new problem)
- Solution (layers, framework, or approach)
- Wrap Up (restate, call to reflection)

**5. Images.**
While writing, flag each place an image or diagram belongs and what it should show. Batch all image generation prompts at the end of the writing session.

**6. Diagrams.**
Use mermaid for flow diagrams. Keep edge labels simple — no colons or commas inside `|label|`.

**7. LinkedIn export.**
Use `scripts/gen-assets.py` to prepare any article for LinkedIn. Run from the repo root:

```bash
python3 scripts/gen-assets.py src/<article>.md           # diagrams + code images
python3 scripts/gen-assets.py src/<article>.md --no-code # diagrams only
```

Output goes to `linkedin/<slug>/` (gitignored):

- `article.txt`: paste-ready text with `[IMAGE: filename]` placeholders everywhere an image belongs
- `diagram-N.png`: rendered mermaid diagrams (via `mermaid-cli`)
- `code-N-<lang>.png`: syntax-highlighted code blocks (via `charm-freeze`, dracula theme) — omitted with `--no-code`

Existing inline images (`![](img/...)`) become placeholders in the text pointing at their original filename. Upload those from `src/img/<slug>/` when composing on LinkedIn.

Manual run-output screenshots (terminal captures) are not generated by the script. Make those separately and store in `src/img/<slug>/`.

## Before Writing Content

Read `~/notes/personal/projects/blog/ai-article-workflow.md` before drafting or editing any article content.

## Agent skills

### Issue tracker

Issues live in GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context repo: one `CONTEXT.md` + `docs/adr/` at root. See `docs/agents/domain.md`.
