---
title: "Tool Use"
chapter: 05
status: draft
summary: "Notes and examples for the Tool Use pattern — using external tools (search, calculators, code execution) to augment model capabilities."
---

# Tool Use

This chapter covers the Tool Use design pattern: composing LLMs with external tools to perform actions they cannot do natively (web search, system commands, calculators, or custom APIs).

Planned sections:
- When to use tools vs. prompt engineering
- Safe tool invocation patterns
- Tool selection and orchestration
- Example: search + synthesis pipeline
- Example: code execution / sandboxing
- Failure modes, retries and verification

Code examples live in `code/chapter_05` and demonstrate both mocked and real tool integrations.
