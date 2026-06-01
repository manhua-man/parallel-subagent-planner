#!/usr/bin/env python3
"""
Result Aggregator

Collects outputs from all subagents, performs basic verification of claims,
and produces a consolidated report.

Verification policy (critical per user profile):
- Subagent self-reports are NOT trusted for side-effects (file creation, GitHub pushes, HTTP calls)
- Always re-verify with terminal/file tools or direct inspection where possible
- Record verification status per task
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AggregatedResult:
    task_id: str
    goal: str
    subagent_summary: str
    verified: bool = False
    verification_notes: str = ""
    artifacts: List[str] = field(default_factory=list)  # file paths, URLs, commit SHAs
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ResultAggregator:
    def __init__(self):
        self.results: List[AggregatedResult] = []

    def add(self, task_id: str, goal: str, subagent_summary: str, artifacts: List[str] = None):
        self.results.append(AggregatedResult(
            task_id=task_id,
            goal=goal,
            subagent_summary=subagent_summary,
            artifacts=artifacts or []
        ))

    def verify(self, task_id: str, verified: bool, notes: str = ""):
        for r in self.results:
            if r.task_id == task_id:
                r.verified = verified
                r.verification_notes = notes
                break

    def final_report(self) -> str:
        lines = ["=== PARALLEL SUBAGENT PLANNER - FINAL REPORT ===\n"]
        for r in self.results:
            status = "✓ VERIFIED" if r.verified else "⚠ UNVERIFIED (self-report only)"
            lines.append(f"[{r.task_id}] {r.goal}")
            lines.append(f"  Status: {status}")
            lines.append(f"  Summary: {r.subagent_summary[:200]}...")
            if r.artifacts:
                lines.append(f"  Artifacts: {', '.join(r.artifacts)}")
            if r.verification_notes:
                lines.append(f"  Verification: {r.verification_notes}")
            lines.append("")
        lines.append(f"Total tasks: {len(self.results)}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "results": [
                {
                    "task_id": r.task_id,
                    "goal": r.goal,
                    "verified": r.verified,
                    "summary": r.subagent_summary,
                    "artifacts": r.artifacts,
                    "notes": r.verification_notes
                } for r in self.results
            ]
        }


if __name__ == "__main__":
    agg = ResultAggregator()
    agg.add("phase-0", "Init repo", "Created README, .gitignore, pushed to GitHub", ["README.md", "https://github.com/..."])
    agg.verify("phase-0", True, "Confirmed via gh repo view and ls")
    print(agg.final_report())