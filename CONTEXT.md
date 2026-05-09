# Blog Project Context

## Glossary

### Agent Loop

The core execution cycle of an agent: call model → check for tool call → execute tool → write observation back to context → repeat. Bounded by a step limit. The loop itself is ~20 lines. Everything else is Harness.

### Code Agent

Default narration term for this repo's articles when referring to a tool-using coding agent. Prefer `code agent` over plain `agent` in article prose. Keep plain `agent` only in direct quotes, citations, file names, and product names.

### Minimal Agent

An agent with only the loop and three tools (list_files, read_file, run_command). No memory, no permission system, no validation. Purpose: anatomy lesson. Shows the skeleton before the harness layers are added.

### Harness

The runtime system surrounding the loop. Comprises five boundaries that make the loop safe and usable in real engineering environments: Tool Boundary, Context Boundary, Memory Boundary, Permission Boundary, Validation Boundary. Not an extra shell — the system that connects the loop to the real world.

### Tool Boundary

Structured tool definitions (name, description, JSON schema). Controls what the model can call, what parameters are valid, and what paths/commands are permitted. Fewer tools = cleaner context = easier to audit.

### Context Boundary

Step limit and timeout. Prevents infinite loops, runaway cost, and context bloat. Minimum viable form: `step < N`.

### Memory Boundary

Layered context management: project rules (persistent), session summary (per-run), procedural memory (learned patterns). Start with Markdown files. Add vector search only when Markdown retrieval is clearly insufficient.

### Permission Boundary

Four tiers: allow / ask / block / log. Controls which tool calls fire automatically vs. require human confirmation. Balances safety against approval fatigue.

### Validation Boundary

Completion is evidence, not tone. An agent saying "done" is not done. Done means: test passed, file written, command exited 0, log recorded.

### Lab Repo

`~/Projects/lab/` — a monorepo for one-time demo projects. Each demo lives in its own subdirectory. Avoids cluttering the GitHub account with stale single-purpose repos.
