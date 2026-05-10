# mdBook AI Navigation Reorganization Design

## Goal

Reorganize the blog's mdBook navigation so the top-level categories reflect current publishing intent:

- `AI` first
- `Coding` second
- `Others` third

The design also introduces a scalable but lightweight structure for AI content, because AI threads are expected to grow faster than the other sections.

## Current State

The current `src/SUMMARY.md` has three main content categories:

- `Coding`
- `AI`
- `Others`

The AI section is a flat list of posts. This works now, but it will become noisy as the number of AI threads increases.

## Desired Outcome

The navigation should support three things:

1. Readers should see `AI` first in the sidebar.
2. New AI threads should be easier to discover than older ones.
3. Older AI threads should stay accessible without turning the sidebar into a dump.

## Recommended Information Architecture

Top-level order:

- `Introduction`
- `AI`
- `Coding`
- `Others`

AI should use a recent-first structure:

- `AI`
- `Latest`
- `Archive 2026`
- future archive pages such as `Archive 2027`

The `Latest` section should contain only the newest `7` AI threads by default. Older AI posts should move into the current year's archive page. The limit can be adjusted later if the sidebar feels too dense or too sparse, but the first implementation should treat `7` as the explicit default.

## Why This Structure

This is the smallest change that still scales.

- It matches the user's publishing priority: AI comes first.
- It keeps fresh material easy to find.
- It avoids premature topic taxonomy inside AI.
- It works naturally with mdBook's static `SUMMARY.md` model.

This is intentionally not a metadata-heavy system. The repo does not need front matter indexing or a full content pipeline for this phase.

## Proposed File Shape

This phase should avoid mass migration.

- Keep existing post files in `src/`
- Keep `src/ai.md` as the AI landing page
- Add `src/ai-latest.md`
- Add yearly archive pages such as `src/ai-archive-2026.md`

Example `SUMMARY.md` shape:

```md
# Summary

- [Introduction](intro.md)

- [AI](ai.md)
  - [Latest](ai-latest.md)
    - [Newest AI Thread](newest-ai-thread.md)
    - [Next AI Thread](next-ai-thread.md)
  - [Archive 2026](ai-archive-2026.md)
    - [Older AI Thread](older-ai-thread.md)

- [Coding](coding.md)
  ...

- [Others](others.md)
  ...
```

## Automation Direction

The user should not need to manually maintain the AI section whenever a new thread is published.

The recommended implementation is:

- keep the AI portion of `src/SUMMARY.md` easy to refresh
- add repo automation that updates the AI navigation structure
- let agents use that automation during commit-oriented workflows

The automation should:

- insert new AI posts into `Latest`
- keep only the newest configured count in `Latest`
- move overflow into the current year's archive
- leave non-AI sections untouched

The automation should be idempotent. Running it when nothing relevant changed should produce no diff.

## Agent Guidance

This should be documented as a soft guidance rule in the repo's agent-facing markdown, with `CLAUDE.md` as the preferred source of truth if present.

Intent of the guidance:

- agents should understand the preferred AI structure
- agents should refresh or fix the AI navigation when it is clearly out of date
- minor drift is acceptable and should not block normal work
- repo automation is preferred over hand-editing the AI navigation block when such automation exists

Suggested wording:

```md
## mdBook Navigation

The blog uses a latest-first structure for AI content in `src/SUMMARY.md`.

Preferred workflow:
- When an agent is preparing a commit that adds or updates AI threads, it should check whether the AI section in `src/SUMMARY.md` still matches the intended structure.
- The preferred AI order is: `Latest` first, then yearly archive pages.
- Minor drift is acceptable. If the navigation is slightly out of date, fix it when noticed instead of treating it as a blocking error.
- Prefer using repo automation to refresh the AI section when available, instead of hand-editing that block.
```

## Non-Goals

This design does not include:

- topic-based AI taxonomy
- moving all posts into nested folders
- generating the entire book structure from front matter
- changing `Coding` or `Others` beyond top-level order

## Implementation Notes

Implementation should be kept narrow:

1. Reorder top-level categories in `src/SUMMARY.md`
2. Add lightweight AI landing and archive pages
3. Add a small refresh mechanism for the AI section
4. Add soft workflow guidance to the repo's agent-facing markdown

## Risks

- If the automation is too clever, it will be harder to trust than a simple static file update.
- If the `Latest` count is too large, the sidebar will drift back toward noise.
- If agent guidance is written as a hard rule, it will create unnecessary friction during normal commits.

These risks are addressed by keeping the system simple, recent-first, and soft-enforced.

## Success Criteria

The change is successful when:

- `AI` appears before `Coding` and `Others`
- the AI section shows newest material first
- older AI threads are archived by year
- normal publishing does not require repetitive manual sidebar maintenance
- agents have clear guidance on how to handle mild navigation drift
