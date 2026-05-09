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

To render diagrams to PNG for LinkedIn, use `mermaid-cli` via Nix (no install needed):

```bash
nix run nixpkgs#mermaid-cli -- -i diagram.mmd -o src/img/<slug>/diagram.png
```

Save each diagram source as a `.mmd` file alongside the PNG so it can be edited later. Store both under `src/img/<slug>/`.

**7. Code screenshots.**
Use `charm-freeze` via Nix to generate syntax-highlighted code images for LinkedIn:

```bash
# pipe a line range from a file into freeze
sed -n '<start>,<end>p' path/to/file.ts | nix run nixpkgs#charm-freeze -- - \
  --language typescript \
  --theme dracula \
  --output src/img/<slug>/snippet-name.png \
  --window \
  --border.radius 8 \
  --shadow.blur 20 \
  --shadow.x 4 \
  --shadow.y 4
```

Store all images under `src/img/<slug>/`. For the blog, embed with `![](img/<slug>/name.png)`. For LinkedIn, attach as images manually.

## Agent skills

### Issue tracker

Issues live in GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context repo: one `CONTEXT.md` + `docs/adr/` at root. See `docs/agents/domain.md`.
