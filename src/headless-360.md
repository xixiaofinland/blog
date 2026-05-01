# Headless 360: The Agent-First Paradigm Shift

I see the same pattern unfolding right now in Salesforce, in AI, in how we build software. And it's happening with Headless 360.

To understand why, let me take you back to the 1950s.

A shipping container was invented. It didn't make cargo ships faster. It didn't make ports more efficient. It did something far more radical: it killed an entire industry.

Before containers, loading cargo was slow and expensive. Armies of dockworkers handled each unique shipment. Ports had to be customized for every cargo type.

Then containers came. They didn't improve break-bulk. They made it obsolete.

Harbors like London and New York fell. Felixstowe rose to replace London's old docks; Port Newark–Elizabeth replaced Manhattan's piers.

Salesforce's Headless 360 is doing the same thing to the "UI-first" paradigm.

They're not iterating from A to A+. They're jumping from A to B. And they made the right call. User interfaces are dying, whether we like it or not.

But let's be clear: **the vision is not enough. The implementation is the key.**

Anyone can say "agent-first." But most get it wrong. I hate it when an agent tells me to go to a link, click a button in the top right, then do this, then do that. Not because the agent wants to, but because the platform doesn't support headless interaction.

I have a simple rule. If you remove all the UI, the agent should still be able to do the same work successfully as you did in the past. If it can't, the platform isn't agent-first.

The hard part isn't saying "agent-first." It's building it and maintaining it in production. To do that right, you need to rethink the entire architecture. Most people start with APIs and stop there. Let's break down the technical layers in my mind:

## 1. Interface Layer

APIs, CLIs, MCPs, skills. The front door that lets agents enter the platform.

[SF CLI](https://developer.salesforce.com/tools/salesforcecli) is developers' best Tooling. Salesforce is famous with diversifed APIs. MCP servers are popping up too. These are the entry points that agents use to interact with the platform. But just having a CLI or an API isn't enough. The interface needs to be designed for agents, not humans who happen to type commands. When an interface has no context, agents start to guess and hallucinate. That's where the next layer comes in.

## 2. Semantic Layer

This is the one everyone skips. Companies think "just expose an API" is enough. But the semantics inside are often terrible. Agents end up guessing, trying multiple paths, and worst of all, triggering side effects they can't see because the interface never explicitly said "this launches a missile to destroy NY city."

Good semantics are the difference between an agent that works and one that doesn't. Think about it:

- CLI tools with really good command and subcommand help menus, not just a one-liner
- MCP servers with incremental discovery, so agents can explore what's available without guessing
- APIs with multi-layer schema descriptions that explain not just what the endpoint does, but when to use it
- Machine-readable manifests like `llm.txt` that give agents a clear map of the platform without reading through pages of human documentation

These all serve the same goal: making the interface understandable to machines, not just humans.

## 3. Core Logic Layer

Flows, Apex, triggers, integrations, the database. The existing business logic that makes the platform valuable. The challenge isn't exposing it. It's making it agent-composable.

## 4. Trust Layer

Yes, platforms eventually add auditing. Everyone knows that's needed. But what they ignore is agent-native observability: logging at a depth humans never would, plus an agent-friendly error API so agents can submit rich diagnostics when tasks fail. Agents are way more willing to give detailed feedback than humans. If your platform doesn't have a way to ingest that, you're throwing away a huge improvement loop.

## 5. Agentic Layer

Agents that manage the platform itself. Observing and monitoring all incoming agent actions, tracking performance, doing A/B testing, scoring behavior, handling version control, and rolling back, all automatically.

## The Hardest Layers

The hardest layers to build are 2 and 4. And they're the easiest to ignore.

Without semantics, agents are guessing. Without trust, agents are a liability.

Salesforce built its empire on low-code, no-code UIs. That paradigm is ending. For developers, architects, and platform owners, the skills that got you here won't take you there. The old paradigms are becoming relics. The question isn't whether to embrace agent-first. It's how fast you can adapt.

Just like the container revolution: some harbors reinvent themselves and thrive. Others become relics.

But let me be clear again: **the vision is not enough. The implementation is the key.** Anyone can say "agent-first." The real work is in the layers.
