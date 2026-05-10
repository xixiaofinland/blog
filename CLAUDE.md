# Blog Agent Notes

This file is the source of truth for agent-specific guidance that may be synced into `AGENTS.md`.

## mdBook Navigation

The blog uses a latest-first structure for AI content in `src/SUMMARY.md`.

Preferred workflow:

- When an agent is preparing a commit that adds or updates AI threads, it should check whether the AI section in `src/SUMMARY.md` still matches the intended structure.
- The preferred AI order is: `Latest` first, then yearly archive pages.
- Minor drift is acceptable. If the navigation is slightly out of date, fix it when noticed instead of treating it as a blocking error.
- Prefer using `python3 scripts/refresh_ai_navigation.py` to refresh the AI section instead of hand-editing that block.
- When adding a new AI thread and you want it in the latest list immediately, use `python3 scripts/refresh_ai_navigation.py --add src/<file>.md`.
