"""Semantic Scholar API client."""

import requests
import time
from typing import List, Dict, Optional, Any
from config import SEMANTIC_SCHOLAR_API_KEY, SEMANTIC_SCHOLAR_BASE, API_TIMEOUT, MAX_PAPERS_PER_SEARCH
from models import Paper
import logging

logger = logging.getLogger(__name__)


class SemanticScholarClient:
    """Client for Semantic Scholar API."""

    def __init__(self, api_key: str = SEMANTIC_SCHOLAR_API_KEY):
        self.api_key = api_key
        self.base_url = SEMANTIC_SCHOLAR_BASE
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": api_key,
            "User-Agent": "ScholAR/1.0"
        })

    def search_papers(self, query: str, limit: int = MAX_PAPERS_PER_SEARCH) -> List[Paper]:
        """Search for papers using semantic scholar."""
        try:
            url = f"{self.base_url}/paper/search"
            params = {
                "query": query,
                "limit": limit,
                "fields": "paperId,title,authors,year,abstract,citationCount,url,references"
            }

            response = self.session.get(url, params=params, timeout=API_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            papers = []
            for item in data.get("data", []):
                paper = self._parse_paper(item)
                if paper:
                    papers.append(paper)

            logger.info(f"Found {len(papers)} papers for query: {query}")
            return papers
        except Exception as e:
            logger.error(f"Error searching papers: {e}")
            return []

    def get_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """Get detailed paper information by ID."""
        try:
            url = f"{self.base_url}/paper/{paper_id}"
            params = {
                "fields": "paperId,title,authors,year,abstract,citationCount,url,references,venueType"
            }

            response = self.session.get(url, params=params, timeout=API_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            return self._parse_paper(data)
        except Exception as e:
            logger.error(f"Error getting paper {paper_id}: {e}")
            return None

    def get_cited_by(self, paper_id: str, limit: int = 10) -> List[Paper]:
        """Get papers that cite this paper."""
        try:
            url = f"{self.base_url}/paper/{paper_id}/citations"
            params = {
                "limit": limit,
                "fields": "paperId,title,authors,year,abstract,citationCount,url"
            }

            response = self.session.get(url, params=params, timeout=API_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            papers = []
            for item in data.get("data", []):
                if "citingPaper" in item:
                    paper = self._parse_paper(item["citingPaper"])
                    if paper:
                        papers.append(paper)

            return papers
        except Exception as e:
            logger.error(f"Error getting citations for {paper_id}: {e}")
            return []

    def _parse_paper(self, data: Dict[str, Any]) -> Optional[Paper]:
        """Parse paper data from API response."""
        try:
            paper_id = data.get("paperId", "")
            title = data.get("title", "")

            if not paper_id or not title:
                return None

            authors = [author.get("name", "") for author in data.get("authors", [])]
            year = data.get("year", 0)
            abstract = data.get("abstract", "")
            url = data.get("url", "")
            citations = data.get("citationCount", 0)

            references = []
            for ref in data.get("references", []):
                if ref.get("paperId"):
                    references.append(ref["paperId"])

            return Paper(
                paper_id=paper_id,
                title=title,
                authors=authors,
                year=year,
                abstract=abstract,
                url=url,
                citations=citations,
                references=references
            )
        except Exception as e:
            logger.error(f"Error parsing paper data: {e}")
            return None

    def close(self):
        """Close the session."""
        self.session.close()
