"""Data models for ScholAR."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class Paper:
    """Represents a research paper."""
    paper_id: str
    title: str
    authors: List[str]
    year: int
    abstract: str
    url: str
    citations: int = 0
    references: List[str] = field(default_factory=list)
    methodology: Optional[str] = None
    main_conclusion: Optional[str] = None
    key_concepts: List[str] = field(default_factory=list)

    def __hash__(self):
        return hash(self.paper_id)

    def __eq__(self, other):
        return isinstance(other, Paper) and self.paper_id == other.paper_id


@dataclass
class ResearchCluster:
    """Represents a cluster of related papers."""
    cluster_id: str
    name: str
    papers: List[Paper] = field(default_factory=list)
    methodology: Optional[str] = None
    year_range: tuple = field(default_factory=tuple)
    key_themes: List[str] = field(default_factory=list)


@dataclass
class Contradiction:
    """Represents a contradiction between papers."""
    paper_a_id: str
    paper_b_id: str
    claim_a: str
    claim_b: str
    topic: str
    confidence: float


@dataclass
class ResearchGap:
    """Represents a research gap identified in the literature."""
    gap_id: str
    description: str
    related_papers: List[str]
    suggested_methodology: Optional[str] = None
    importance_score: float = 0.5


@dataclass
class AgentThought:
    """Represents an agent's thought/decision log."""
    timestamp: datetime
    thought_type: str  # 'decision', 'observation', 'reasoning', 'action'
    message: str
    context: Dict[str, Any] = field(default_factory=dict)

    def __str__(self):
        emoji_map = {
            'decision': '[DECISION]',
            'observation': '[OBSERVATION]',
            'reasoning': '[REASONING]',
            'action': '[ACTION]'
        }
        marker = emoji_map.get(self.thought_type, '*')
        return f"{marker} {self.message}"


@dataclass
class ResearchAnalysis:
    """Final research analysis result."""
    query: str
    papers: List[Paper]
    clusters: List[ResearchCluster]
    contradictions: List[Contradiction]
    research_gaps: List[ResearchGap]
    trends: Dict[int, List[str]]  # Year -> themes
    thought_log: List[AgentThought]
    saturation_score: float
    next_steps_proposal: Optional[str] = None
    limitations: Optional[str] = None
