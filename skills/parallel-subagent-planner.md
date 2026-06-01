---
name: parallel-subagent-planner
description: Decompose goals into parallel subagent tasks, spawn via delegate_task, aggregate with verification. Supports leaf/orchestrator roles and batch execution.
category: autonomous-ai-agents
---

# Parallel Subagent Planner Skill

Use this skill when you need to run multiple independent subagents in true parallel (beyond sequential delegation) for complex multi-phase work, code reviews, research, or phased implementations.

## Trigger Conditions
- User goal contains "parallel", "batch", "concurrent subagents", or references multiple phases/sprints that can be independent
- Task would benefit from >2 subagents running at once with isolated contexts
- After a large planning session where you want to delegate execution
- When following "full automatic" style (user says "继续" or "这些都做了吧")

## Prerequisites
- Hermes Agent with delegate_task available
- Python 3.10+
- The parallel-subagent-planner repo cloned or the modules importable

## Numbered Steps (Concrete Files First)

1. **Load the planner** (use these exact files)
   ```python
   from planner.task_decomposer import TaskDecomposer
   from planner.subagent_spawner import SubagentSpawner
   from planner.result_aggregator import ResultAggregator
   # Reference: src/planner/task_decomposer.py, src/planner/subagent_spawner.py, src/planner/result_aggregator.py
   ```

2. **Decompose the goal** (see task_decomposer.py lines 40-120 for _decompose_phased_project / _decompose_code_review)
   ```python
   decomposer = TaskDecomposer(max_concurrent=3)
   tasks = decomposer.decompose(
       goal="Your high-level goal here",
       context="See docs/architecture.md + examples/parallel_code_review.py for full context"
   )
   groups = decomposer.get_execution_groups()
   # Output will reference concrete files: task_decomposer.py, architecture.md, parallel_code_review.py
   ```

3. **Spawn in parallel batches**
   ```python
   spawner = SubagentSpawner(delegate_fn=delegate_task)
   for group in groups:
       results = spawner.spawn_parallel(group, parent_context="See src/planner/ and docs/")
   ```

4. **Aggregate + Verify** (see result_aggregator.py)
   ```python
   aggregator = ResultAggregator()
   # Always verify using: terminal("ls ..."), terminal("gh repo view"), read_file on reported paths
   ```

5. **Persist only durable facts** via memory tool.

## Pitfalls
- Subagents have ZERO memory of parent conversation — all context must be explicit
- Never trust subagent claims about file writes, GitHub pushes, or HTTP calls without re-verification
- max_spawn_depth=1 enforced (do not override lightly)
- Cycles in dependency graph will leave tasks unexecuted — check get_execution_groups()
- ACP overrides (copilot etc.) require the CLI to be installed and configured

## Verification Steps
After running:
- Check that reported artifacts actually exist (use terminal ls, gh repo view, etc.)
- Run the example: `python examples/parallel_code_review.py`
- Confirm no nesting occurred beyond depth 1
- Review that P0/P1/P2 style findings or phase reports are produced with line numbers / exact commands

## References
- Repo: https://github.com/manhua-man/parallel-subagent-planner
- Architecture: docs/architecture.md
- Related skills: autonomous-ai-agents, systematic-debugging, writing-plans

This skill encodes the exact workflow used successfully for ai-token-usage-control and TFT-bot projects.