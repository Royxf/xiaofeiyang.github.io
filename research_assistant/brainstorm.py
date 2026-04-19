from __future__ import annotations

from dataclasses import dataclass

from .providers import Paper


@dataclass(slots=True)
class IdeaCard:
    title: str
    hypothesis: str
    experiment: str
    risk: str


class BrainstormEngine:
    """Generate idea cards from searched papers."""

    def generate(self, topic: str, papers: list[Paper], max_cards: int = 3) -> list[IdeaCard]:
        cards: list[IdeaCard] = []
        for index, paper in enumerate(papers[:max_cards], start=1):
            gap = self._extract_gap(paper.abstract)
            cards.append(
                IdeaCard(
                    title=f"Idea {index}: {topic} + {paper.source}",
                    hypothesis=f"If we target '{gap}', the method can improve robustness on out-of-domain tasks.",
                    experiment=(
                        "1) Reproduce baseline; 2) add gap-focused module; "
                        "3) compare on held-out split and ablation settings."
                    ),
                    risk="Potential dataset leakage or overfitting; require cross-dataset validation.",
                )
            )
        return cards

    @staticmethod
    def _extract_gap(abstract: str) -> str:
        if not abstract:
            return "insufficient evidence in prior work"
        lowered = abstract.lower()
        signals = ["challenge", "gap", "failure", "future work", "limitations"]
        for signal in signals:
            if signal in lowered:
                return f"the '{signal}' direction noted by prior studies"
        return "unresolved robustness and generalization limitations"
