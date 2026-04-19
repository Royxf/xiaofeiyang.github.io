import unittest

from research_assistant.model import ResearchOrchestrator
from research_assistant.providers import MockProvider
from research_assistant.store import KnowledgeStore


class ResearchAssistantTest(unittest.TestCase):
    def test_offline_pipeline(self):
        store = KnowledgeStore(path="data/test_research_wiki.json")
        orchestrator = ResearchOrchestrator(providers=[MockProvider()], store=store)

        result = orchestrator.run(topic="multi-agent literature review", limit_per_provider=2, cards=2)

        self.assertEqual(result["topic"], "multi-agent literature review")
        self.assertEqual(len(result["papers"]), 2)
        self.assertEqual(len(result["ideas"]), 2)


if __name__ == "__main__":
    unittest.main()
