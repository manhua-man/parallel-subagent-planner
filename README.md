# Parallel Subagent Planner

A repository for planning, orchestrating, and executing parallel subagent workflows in Hermes Agent and compatible AI coding agent systems.

## Overview

This project provides tools, patterns, and a planner implementation for running multiple subagents in parallel. It leverages delegation mechanisms (e.g., delegate_task) to distribute tasks across independent agent instances with isolated contexts, terminals, and toolsets.

Key features planned:
- Task decomposition for parallel execution
- Subagent lifecycle management (leaf vs orchestrator roles)
- Context isolation and result aggregation
- Integration with Hermes delegation, Claude Code, OpenCode, Codex CLIs
- Scheduling via cronjob for recurring parallel runs
- Verification, error handling, and result merging

## Project Structure

```
parallel-subagent-planner/
├── README.md
├── docs/
│   ├── architecture.md
│   ├── delegation-patterns.md
│   └── examples/
├── src/
│   ├── planner/
│   │   ├── task_decomposer.py
│   │   ├── subagent_spawner.py
│   │   └── result_aggregator.py
│   └── cli.py
├── tests/
├── examples/
│   └── parallel_code_review.py
└── skills/
    └── parallel-subagent-planner.md
```

## Goals

- Enable true parallelism beyond sequential delegation
- Reduce user steering by providing durable planning memory
- Support complex multi-phase projects (like the ai-token-usage-control and TFT-bot examples in history)
- Provide reusable skills and templates

## Getting Started

1. Clone the repo
2. Install dependencies (TBD based on language choice - Python primary)
3. Use the planner CLI or import as skill in Hermes

See docs/architecture.md for detailed design.

## Status

Initial skeleton created. Next: detailed planning phase, architecture doc, core implementation.

License: MIT
Author: manhua-man
```

This matches the preference for detailed documentation.