#!/usr/bin/env python3
"""
Subagent Spawner

Wraps delegate_task calls for the Parallel Subagent Planner.
Handles role assignment, context injection, toolset restriction, and nesting safety.

Key rules enforced:
- max_spawn_depth=1 by default (global safety)
- Subagents receive NO parent conversation memory
- All context must be explicitly passed
- Verification of side-effects is the caller's responsibility (see Result Aggregator)
"""

from typing import List, Dict, Any, Optional
from .task_decomposer import Task


class SubagentSpawner:
    def __init__(self, delegate_fn=None):
        """
        delegate_fn: the actual delegate_task implementation (injected for testability).
        In real Hermes runtime this would be the built-in delegate_task.
        """
        self.delegate_fn = delegate_fn or self._mock_delegate
        self.spawned: List[Dict[str, Any]] = []

    def _mock_delegate(self, **kwargs) -> Dict[str, Any]:
        """Placeholder until running inside Hermes with real delegate_task."""
        print(f"[MOCK DELEGATE] Would spawn subagent with: {list(kwargs.keys())}")
        return {"status": "mock", "summary": f"Mock result for goal: {kwargs.get('goal', 'unknown')[:60]}..."}

    def spawn(self, task: Task, parent_context: str = "") -> Dict[str, Any]:
        """
        Spawn one subagent for the given task.
        Returns the raw result dict from delegate_task.
        """
        full_context = f"{parent_context}\n\n--- TASK CONTEXT ---\n{task.context}".strip()

        payload = {
            "goal": task.goal,
            "context": full_context,
            "toolsets": task.toolsets,
            "role": task.role,
            "max_spawn_depth": task.max_spawn_depth,
        }
        if task.acp_command:
            payload["acp_command"] = task.acp_command

        result = self.delegate_fn(**payload)
        self.spawned.append({
            "task_id": task.id,
            "goal": task.goal,
            "result": result
        })
        return result

    def spawn_parallel(self, tasks: List[Task], parent_context: str = "") -> List[Dict[str, Any]]:
        """
        Spawn a batch of independent tasks (already verified to have no inter-dependencies).
        In real system these would run concurrently via Hermes delegation batching.
        """
        results = []
        for task in tasks:
            res = self.spawn(task, parent_context)
            results.append(res)
        return results

    def get_summary(self) -> str:
        return f"Spawned {len(self.spawned)} subagents. Last: {self.spawned[-1]['task_id'] if self.spawned else 'none'}"


if __name__ == "__main__":
    from .task_decomposer import TaskDecomposer
    decomposer = TaskDecomposer()
    tasks = decomposer.decompose("Build parallel planner skeleton")
    spawner = SubagentSpawner()
    results = spawner.spawn_parallel(tasks[:2])
    print(spawner.get_summary())
    print("Results:", results)