#!/usr/bin/env python3
"""
Task Decomposer for Parallel Subagent Planner

Breaks a high-level goal into independent, parallelizable tasks.
Produces a dependency graph so the spawner can run non-dependent tasks concurrently.

Design principles (from user profile + architecture):
- Detailed, explicit code with root-cause style comments
- Supports batch parallelism up to delegation.max_concurrent_children
- Returns structured tasks that carry full context for subagents
- Never assumes shared state between tasks

Input: goal string + optional constraints (toolsets, max_depth, etc.)
Output: list of Task objects + execution order groups
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
import json


@dataclass
class Task:
    """Single unit of work for one subagent (leaf or orchestrator)."""
    id: str
    goal: str
    context: str  # Full background the subagent needs (file paths, errors, constraints)
    toolsets: List[str] = field(default_factory=lambda: ["terminal", "file"])
    role: str = "leaf"  # "leaf" or "orchestrator"
    dependencies: List[str] = field(default_factory=list)  # task ids that must finish first
    max_spawn_depth: int = 1
    acp_command: Optional[str] = None  # e.g. "copilot" for ACP override


class TaskDecomposer:
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.tasks: Dict[str, Task] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}  # id -> set of dependents

    def decompose(self, goal: str, context: str = "", toolsets: Optional[List[str]] = None) -> List[Task]:
        """
        Main entry point. Decomposes goal into parallel tasks.

        Current implementation: heuristic decomposition for common patterns
        (code review, multi-phase implementation, research + implementation).
        Future: LLM-assisted decomposition with verification.
        """
        if toolsets is None:
            toolsets = ["terminal", "file", "web"]

        tasks: List[Task] = []

        # Pattern 1: Multi-phase project (e.g. "build X with phases 0-3")
        if any(kw in goal.lower() for kw in ["phase", "sprint", "stage", "implement"]):
            tasks = self._decompose_phased_project(goal, context, toolsets)

        # Pattern 2: Code review / audit across many files
        elif any(kw in goal.lower() for kw in ["review", "audit", "inspect", "verify"]):
            tasks = self._decompose_code_review(goal, context, toolsets)

        # Pattern 3: Parallel research + synthesis
        elif any(kw in goal.lower() for kw in ["research", "explore", "compare"]):
            tasks = self._decompose_research(goal, context, toolsets)

        # Default: single task (no parallelism)
        else:
            tasks = [Task(
                id="task-0",
                goal=goal,
                context=context,
                toolsets=toolsets,
                role="leaf"
            )]

        # Build internal structures
        for t in tasks:
            self.tasks[t.id] = t
            self.dependency_graph[t.id] = set()

        # Populate reverse dependencies
        for t in tasks:
            for dep in t.dependencies:
                if dep in self.dependency_graph:
                    self.dependency_graph[dep].add(t.id)

        return tasks

    def _decompose_phased_project(self, goal: str, context: str, toolsets: List[str]) -> List[Task]:
        """Example: split into Phase 0 (setup), Phase 1 (core), Phase 2 (tests), Phase 3 (docs)"""
        base_context = f"Project goal: {goal}\n{context}\nFollow strict phase ordering. Report exact file paths and verification commands used."

        phase0 = Task(
            id="phase-0",
            goal="Project initialization, directory structure, git init, basic README and .gitignore",
            context=base_context,
            toolsets=toolsets,
            role="leaf",
            dependencies=[]
        )
        phase1 = Task(
            id="phase-1",
            goal="Core implementation of the main feature (see architecture.md for details)",
            context=base_context + "\nDepends on Phase 0 skeleton being present.",
            toolsets=toolsets,
            role="leaf",
            dependencies=["phase-0"]
        )
        phase2 = Task(
            id="phase-2",
            goal="Write unit tests + integration tests. Verify with pytest or equivalent.",
            context=base_context + "\nPhase 1 code must exist. Use systematic-debugging style if tests fail.",
            toolsets=toolsets,
            role="leaf",
            dependencies=["phase-1"]
        )
        phase3 = Task(
            id="phase-3",
            goal="Documentation, architecture diagrams if needed, final README updates, git commit",
            context=base_context + "\nAll previous phases complete. Include verification steps.",
            toolsets=toolsets,
            role="leaf",
            dependencies=["phase-2"]
        )
        return [phase0, phase1, phase2, phase3]

    def _decompose_code_review(self, goal: str, context: str, toolsets: List[str]) -> List[Task]:
        """Parallel review of different modules / concerns"""
        base = f"Code review task: {goal}\n{context}\nFor each file produce P0/P1/P2 findings with exact line numbers and root cause."

        t1 = Task(id="review-core", goal="Review core logic and runtime correctness", context=base, toolsets=toolsets, dependencies=[])
        t2 = Task(id="review-async", goal="Review async patterns, variable scoping, double-dispatch risks", context=base, toolsets=toolsets, dependencies=[])
        t3 = Task(id="review-security", goal="Review security (shell-arg, auth, file writes, network calls)", context=base, toolsets=toolsets, dependencies=[])
        t4 = Task(id="review-package", goal="Review package manifest, .vscodeignore, source pointers, build artifacts", context=base, toolsets=toolsets, dependencies=[])

        # All independent -> can run fully parallel
        return [t1, t2, t3, t4]

    def _decompose_research(self, goal: str, context: str, toolsets: List[str]) -> List[Task]:
        t1 = Task(id="research-arxiv", goal=f"Search arXiv and academic sources for: {goal}", context=context, toolsets=["web"], dependencies=[])
        t2 = Task(id="research-code", goal=f"Find reference implementations and existing Hermes skills for: {goal}", context=context, toolsets=toolsets, dependencies=[])
        t3 = Task(id="research-examples", goal=f"Locate real-world usage patterns and pitfalls for: {goal}", context=context, toolsets=toolsets, dependencies=[])
        return [t1, t2, t3]

    def get_execution_groups(self) -> List[List[Task]]:
        """
        Returns tasks grouped by dependency level.
        Groups can be executed in parallel (within max_concurrent limit).
        """
        groups: List[List[Task]] = []
        completed: Set[str] = set()

        while len(completed) < len(self.tasks):
            ready = []
            for tid, task in self.tasks.items():
                if tid in completed:
                    continue
                if all(dep in completed for dep in task.dependencies):
                    ready.append(task)

            if not ready:
                # Cycle or unmet dep - return what we have
                break

            # Respect concurrency limit
            groups.append(ready[:self.max_concurrent])
            for t in ready[:self.max_concurrent]:
                completed.add(t.id)

        return groups

    def to_json(self) -> str:
        return json.dumps({
            "tasks": [t.__dict__ for t in self.tasks.values()],
            "execution_groups": [[t.id for t in g] for g in self.get_execution_groups()]
        }, indent=2)


if __name__ == "__main__":
    # Self-test
    decomposer = TaskDecomposer(max_concurrent=3)
    tasks = decomposer.decompose(
        goal="Implement parallel subagent planner with phases",
        context="Repo at /c/Users/ManHua/parallel-subagent-planner. Use existing Hermes delegate_task patterns."
    )
    print(decomposer.to_json())
    print("\nExecution order groups:")
    for i, group in enumerate(decomposer.get_execution_groups()):
        print(f"  Group {i}: {[t.id for t in group]}")