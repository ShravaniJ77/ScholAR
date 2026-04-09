"""OpenRouter LLM client for intelligent analysis."""

import requests
import json
from typing import Optional, List, Dict, Any
from config import OPENROUTER_API_KEY, OPENROUTER_BASE, LLM_TIMEOUT, FAST_MODEL, SMART_MODEL
import logging

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """Client for OpenRouter API for LLM calls."""

    def __init__(self, api_key: str = OPENROUTER_API_KEY):
        self.api_key = api_key
        self.base_url = OPENROUTER_BASE

    def call_model(
        self,
        prompt: str,
        model: str = FAST_MODEL,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """Call LLM via OpenRouter."""
        try:
            messages = []

            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            messages.append({
                "role": "user",
                "content": prompt
            })

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "https://github.com/anthropics/claude-code",
                    "X-Title": "ScholAR"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "top_p": 0.9
                },
                timeout=LLM_TIMEOUT
            )

            response.raise_for_status()
            data = response.json()

            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0].get("message", {}).get("content", "")
                return content.strip()

            logger.error(f"Unexpected response format: {data}")
            return None

        except requests.exceptions.Timeout:
            logger.error("LLM request timed out")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return None

    def extract_methodology(self, abstract: str, title: str) -> Optional[str]:
        """Extract methodology from a paper's abstract."""
        prompt = f"""Analyze this research paper and extract the PRIMARY METHODOLOGY in 1-2 sentences.

Title: {title}
Abstract: {abstract}

Focus on the METHOD/TECHNIQUE used, not the results. Be concise."""

        return self.call_model(
            prompt,
            model=FAST_MODEL,
            max_tokens=200,
            temperature=0.3
        )

    def extract_conclusion(self, abstract: str, title: str) -> Optional[str]:
        """Extract main conclusion from a paper's abstract."""
        prompt = f"""Extract the MAIN CONCLUSION or KEY FINDING from this paper in 1-2 sentences.

Title: {title}
Abstract: {abstract}

Be concise and factual."""

        return self.call_model(
            prompt,
            model=FAST_MODEL,
            max_tokens=150,
            temperature=0.3
        )

    def identify_contradictions(self, conclusions_dict: Dict[str, str]) -> Optional[str]:
        """Identify contradictions between papers."""
        conclusions_text = "\n".join([
            f"Paper {idx}: {conclusion}"
            for idx, conclusion in conclusions_dict.items()
        ])

        prompt = f"""Analyze these paper conclusions for CONTRADICTIONS or CONFLICTING CLAIMS:

{conclusions_text}

List each contradiction found with the paper IDs involved. Format as:
- Paper X vs Paper Y: [Statement of contradiction]

If no contradictions, respond: "No clear contradictions found."
"""

        return self.call_model(
            prompt,
            model=SMART_MODEL,
            max_tokens=800,
            temperature=0.5
        )

    def identify_research_gaps(self, abstracts: List[str], titles: List[str]) -> Optional[str]:
        """Identify research gaps based on paper collection."""
        papers_text = "\n".join([
            f"{idx + 1}. {title}\n   {abstract[:200]}..."
            for idx, (title, abstract) in enumerate(zip(titles, abstracts))
        ])

        prompt = f"""Review this collection of research papers and identify 3-5 KEY RESEARCH GAPS:

{papers_text}

For each gap, state:
- What's missing from current research
- Why it matters
- Suggested methodology to address it

Format as:
## Gap [Number]: [Title]
Description: [...]
Suggested Approach: [...]
"""

        return self.call_model(
            prompt,
            model=SMART_MODEL,
            max_tokens=1000,
            temperature=0.6
        )

    def generate_trend_analysis(self, papers_by_year: Dict[int, List[str]]) -> Optional[str]:
        """Generate trend analysis over years."""
        timeline_text = "\n".join([
            f"Year {year}: {', '.join(themes[:5])}"
            for year, themes in sorted(papers_by_year.items())
        ])

        prompt = f"""Analyze how research trends have evolved based on this timeline:

{timeline_text}

Describe:
1. Key methodological shifts over time
2. Emerging focus areas
3. Declining research directions
4. Overall trajectory of the field

Be concise but insightful."""

        return self.call_model(
            prompt,
            model=SMART_MODEL,
            max_tokens=800,
            temperature=0.6
        )

    def generate_grant_proposal(self, gaps: str, field: str) -> Optional[str]:
        """Generate a grant proposal based on identified gaps."""
        prompt = f"""Based on these research gaps in {field}, generate a brief GRANT PROPOSAL for next research steps:

{gaps}

Include:
1. Research Question
2. Proposed Methodology
3. Expected Outcomes
4. Budget Justification (brief)

Keep it concise but compelling."""

        return self.call_model(
            prompt,
            model=SMART_MODEL,
            max_tokens=800,
            temperature=0.7
        )

    def devil_advocate_review(self, literature_review: str) -> Optional[str]:
        """Play devil's advocate on the generated report."""
        prompt = f"""You are a critical reviewer. Analyze this literature review and identify:
1. Missing perspectives or contradictions being ignored
2. Potential biases in the research selection
3. Blind spots or untested assumptions
4. Alternative interpretations of the findings

Literature Review:
{literature_review}

Provide a critical analysis that challenges the synthesis."""

        return self.call_model(
            prompt,
            model=SMART_MODEL,
            max_tokens=600,
            temperature=0.7
        )

    def extract_key_concepts(self, abstract: str) -> Optional[str]:
        """Extract key concepts from abstract."""
        prompt = f"""Extract 5-7 KEY CONCEPTS or TERMS from this abstract as a comma-separated list:

{abstract}

Only the concepts, no explanations."""

        return self.call_model(
            prompt,
            model=FAST_MODEL,
            max_tokens=100,
            temperature=0.3
        )
