#!/usr/bin/env python3
"""
Example: Parallel code review using the planner.

Demonstrates full flow:
1. Decompose review goal into independent tasks
2. Spawn subagents in parallel batches
3. Aggregate + verify results
"""

import sys
sys.path.insert(0, "../src")

from planner import TaskDecomposer, SubagentSpawner, ResultAggregator


def main():
    goal = "Perform thorough P0/P1/P2 code review of the parallel-subagent-planner source"
    context = "Focus on runtime correctness, async scoping, security (shell args), package integrity. Reference ai-token-usage-control review style."

    decomposer = TaskDecomposer(max_concurrent=4)
    tasks = decomposer.decompose(goal, context=context)

    print("Decomposed into tasks:")
    for t in tasks:
        print(f"  - {t.id}: {t.goal} (deps: {t.dependencies})")

    spawner = SubagentSpawner()  # mock for demo
    aggregator = ResultAggregator()

    groups = decomposer.get_execution_groups()
    for i, group in enumerate(groups):
        print(f"\n=== Executing group {i} ({len(group)} tasks) ===")
        results = spawner.spawn_parallel(group, parent_context=context)
        for task, res in zip(group, results):
            summary = res.get("summary", str(res))
            aggregator.add(task.id, task.goal, summary, artifacts=[])
            # In real run we would call aggregator.verify(...) after terminal checks

    print("\n" + aggregator.final_report())


if __name__ == "__main__":
    main()