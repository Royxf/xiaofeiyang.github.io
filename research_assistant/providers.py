from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


@dataclass(slots=True)
class Paper:
    source: str
    paper_id: str
    title: str
    abstract: str
    url: str
    published_at: str
    citations: int = 0


class PaperProvider:
    """Base provider protocol."""

    name = "base"

    def search(self, query: str, limit: int = 5) -> list[Paper]:
        raise NotImplementedError


class ArxivProvider(PaperProvider):
    name = "arxiv"
    endpoint = "https://export.arxiv.org/api/query"

    def search(self, query: str, limit: int = 5) -> list[Paper]:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max(1, min(limit, 20)),
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        url = f"{self.endpoint}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=15) as response:
            data = response.read().decode("utf-8")

        root = ET.fromstring(data)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        papers: list[Paper] = []
        for entry in root.findall("atom:entry", ns):
            paper_id = entry.findtext("atom:id", default="", namespaces=ns).strip()
            title = " ".join(entry.findtext("atom:title", default="", namespaces=ns).split())
            abstract = " ".join(entry.findtext("atom:summary", default="", namespaces=ns).split())
            published_raw = entry.findtext("atom:published", default="", namespaces=ns)
            published_at = _normalize_date(published_raw)
            papers.append(
                Paper(
                    source=self.name,
                    paper_id=paper_id,
                    title=title,
                    abstract=abstract,
                    url=paper_id,
                    published_at=published_at,
                )
            )
        return papers


class SemanticScholarProvider(PaperProvider):
    name = "semantic_scholar"
    endpoint = "https://api.semanticscholar.org/graph/v1/paper/search"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key

    def search(self, query: str, limit: int = 5) -> list[Paper]:
        params = {
            "query": query,
            "limit": max(1, min(limit, 20)),
            "fields": "paperId,title,abstract,url,year,citationCount",
            "sort": "publicationDate:desc",
        }
        url = f"{self.endpoint}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url)
        if self.api_key:
            req.add_header("x-api-key", self.api_key)

        with urllib.request.urlopen(req, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))

        papers: list[Paper] = []
        for item in payload.get("data", []):
            year = item.get("year")
            papers.append(
                Paper(
                    source=self.name,
                    paper_id=item.get("paperId", ""),
                    title=(item.get("title") or "").strip(),
                    abstract=(item.get("abstract") or "").strip(),
                    url=item.get("url") or "",
                    published_at=f"{year}-01-01" if year else "",
                    citations=int(item.get("citationCount") or 0),
                )
            )
        return papers


class MockProvider(PaperProvider):
    """Offline fallback provider to ensure predictable local runs."""

    name = "mock"

    def search(self, query: str, limit: int = 5) -> list[Paper]:
        base = [
            Paper(
                source=self.name,
                paper_id="mock-1",
                title=f"{query}: Survey of Methods",
                abstract="A broad survey discussing current methods, open challenges, and evaluation gaps.",
                url="https://example.org/mock-1",
                published_at="2025-06-01",
                citations=24,
            ),
            Paper(
                source=self.name,
                paper_id="mock-2",
                title=f"{query}: Benchmark and Error Analysis",
                abstract="Presents benchmark experiments and identifies failure cases for future work.",
                url="https://example.org/mock-2",
                published_at="2025-11-11",
                citations=11,
            ),
            Paper(
                source=self.name,
                paper_id="mock-3",
                title=f"{query}: Agentic Workflow Proposal",
                abstract="Introduces a workflow that combines retrieval, synthesis, and iterative brainstorming.",
                url="https://example.org/mock-3",
                published_at="2026-01-20",
                citations=3,
            ),
        ]
        return base[: max(1, min(limit, len(base)))]


def _normalize_date(value: str) -> str:
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return value
