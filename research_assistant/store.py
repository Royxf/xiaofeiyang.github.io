from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .brainstorm import IdeaCard
from .providers import Paper


class KnowledgeStore:
    """Simple JSON knowledge store (append-only by default)."""

    def __init__(self, path: str = "data/research_wiki.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict:
        if not self.path.exists():
            return {"topics": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save_topic(self, topic: str, papers: list[Paper], ideas: list[IdeaCard]) -> dict:
        data = self.load()
        entry = {
            "topic": topic,
            "papers": [asdict(paper) for paper in papers],
            "ideas": [asdict(idea) for idea in ideas],
        }
        topics = data.setdefault("topics", [])

        for i, existed in enumerate(topics):
            if existed.get("topic") == topic:
                topics[i] = entry
                break
        else:
            topics.append(entry)

        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return entry
