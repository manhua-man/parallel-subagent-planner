# Parallel Subagent Planner Architecture

## Core Concepts

### Subagent Roles
- **leaf**: Focused worker. Cannot delegate further. Executes a single goal with provided toolsets and context. Returns a summary.
- **orchestrator**: Can spawn additional subagents using delegate_task. Coordinates parallel workstreams. Bounded by max_spawn_depth (default 1 to prevent uncontrolled nesting).

### Parallel Execution Model
The planner decomposes a high-level goal into independent tasks that can run concurrently. Each task gets:
- Isolated conversation history
- Separate terminal session
- Dedicated toolset subset (e.g., only 'terminal' + 'file' for code tasks)
- Context passed explicitly (file paths, error messages, constraints)

Results are aggregated after all subagents complete. Failures in one branch do not halt others unless configured.

### Key Components
1. **Task Decomposer** (`src/planner/task_decomposer.py`)
   - Breaks complex goals into bite-sized parallelizable tasks
   - Uses dependency graph to determine execution order (independent tasks first)
   - Supports batch mode (up to delegation.max_concurrent_children)

2. **Subagent Spawner** (`src/planner/subagent_spawner.py`)
   - Wraps delegate_task calls
   - Handles role assignment, acp_command overrides, context injection
   - Monitors for nesting violations

3. **Result Aggregator** (`src/planner/result_aggregator.py`)
   - Collects subagent summaries
   - Performs verification (self-reported facts checked via fetch/read where possible)
   - Generates consolidated report with status per task

### Integration Points
- Hermes native delegation (preferred)
- ACP-compatible CLIs (Claude Code, OpenCode, Codex) via overrides
- cronjob skill for scheduled parallel runs (e.g., nightly batch reviews)
- Memory persistence for cross-session task state (only durable facts)

## Constraints & Best Practices
- max_spawn_depth=1 enforced globally in most cases
- Subagents have no memory of parent conversation
- Always verify external side-effects (URLs, file writes, HTTP) before trusting subagent claims
- Use 'web' toolset only when network access is required; prefer 'terminal' + 'file' for local work
- For long-running parallel work, use cronjob with no_agent=true for watchdog scripts

## Data Flow
Goal → Decomposer → Task list + dependency graph → Parallel spawn (batch) → Isolated execution → Aggregator → Final report + memory updates

## Future Extensions
- Visual task graph rendering (mermaid/excalidraw)
- Automatic skill patching from discovered pitfalls during parallel runs
- RL-based task decomposition tuning (tie-in to TFT-bot learnings)

This architecture enables the "full automatic" execution style preferred in user profile while maintaining isolation and verifiability.