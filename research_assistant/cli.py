from __future__ import annotations

import argparse
import json
import os

from .model import ResearchOrchestrator
from .providers import ArxivProvider, MockProvider, SemanticScholarProvider
from .store import KnowledgeStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Academic search and brainstorming assistant")
    parser.add_argument("--topic", required=True, help="Research topic, e.g. 'retrieval-augmented generation'")
    parser.add_argument("--limit", type=int, default=3, help="Per-provider paper count")
    parser.add_argument("--cards", type=int, default=3, help="Brainstorm card count")
    parser.add_argument("--offline", action="store_true", help="Use mock provider only")
    parser.add_argument("--store", default="data/research_wiki.json", help="Path for persistent knowledge store")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.offline:
        providers = [MockProvider()]
    else:
        providers = [
            ArxivProvider(),
            SemanticScholarProvider(api_key=os.getenv("SEMANTIC_SCHOLAR_API_KEY")),
            MockProvider(),
        ]

    orchestrator = ResearchOrchestrator(providers=providers, store=KnowledgeStore(args.store))
    result = orchestrator.run(topic=args.topic, limit_per_provider=args.limit, cards=args.cards)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
