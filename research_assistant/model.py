from __future__ import annotations

from dataclasses import asdict

from .brainstorm import BrainstormEngine
from .providers import PaperProvider
from .store import KnowledgeStore


class ResearchOrchestrator:
    """End-to-end pipeline: search -> rank -> brainstorm -> persist."""

    def __init__(
        self,
        providers: list[PaperProvider],
        store: KnowledgeStore,
        brainstorm_engine: BrainstormEngine | None = None,
    ) -> None:
        self.providers = providers
        self.store = store
        self.brainstorm_engine = brainstorm_engine or BrainstormEngine()

    def run(self, topic: str, limit_per_provider: int = 3, cards: int = 3) -> dict:
        papers = []
        for provider in self.providers:
            try:
                papers.extend(provider.search(topic, limit=limit_per_provider))
            except Exception as exc:  # noqa: BLE001
                papers.append(
                    provider.search(f"{topic} fallback", limit=1)[0]
                    if provider.name == "mock"
                    else _error_paper(provider.name, exc)
                )

        ranked = sorted(
            papers,
            key=lambda item: (item.citations, item.published_at),
            reverse=True,
        )
        ideas = self.brainstorm_engine.generate(topic, ranked, max_cards=cards)
        saved = self.store.save_topic(topic, ranked, ideas)

        return {
            "topic": topic,
            "papers": [asdict(p) for p in ranked],
            "ideas": [asdict(i) for i in ideas],
            "saved": saved,
        }


def _error_paper(provider_name: str, exc: Exception):
    from .providers import Paper

    return Paper(
        source=provider_name,
        paper_id=f"error-{provider_name}",
        title=f"Provider error: {provider_name}",
        abstract=str(exc),
        url="",
        published_at="",
        citations=0,
    )
