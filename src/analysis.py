"""Advanced analysis module for ScholAR research data."""

from collections import Counter
import re


def calculate_paper_quality_score(paper: dict) -> dict:
    """Calculate quality score for a paper based on available metadata."""
    score = 0
    details = []
    max_possible = 120  # We can go over 100, will be capped

    # Check for abstract (worth 25 points)
    abstract = str(paper.get('abstract', ''))
    if abstract and len(abstract) > 200:
        score += 25
        details.append("✓ Comprehensive abstract")
    elif abstract and len(abstract) > 100:
        score += 18
        details.append("✓ Detailed abstract")
    elif abstract:
        score += 10
        details.append("✓ Has abstract")

    # Check for authors (worth 20 points)
    authors = paper.get('authors', [])
    if authors:
        try:
            if isinstance(authors, list):
                author_count = len(authors)
            else:
                author_count = len(str(authors).split(','))

            if author_count >= 5:
                score += 20
                details.append(f"✓ {author_count} co-authors (high collab)")
            elif author_count >= 3:
                score += 16
                details.append(f"✓ {author_count} co-authors")
            elif author_count >= 2:
                score += 12
                details.append(f"✓ {author_count} co-authors")
            else:
                score += 8
                details.append("✓ Single author")
        except:
            pass

    # Check publication year (worth 35 points)
    try:
        year = int(paper.get('year', 0))
        if year > 0:
            current_year = 2024
            years_old = current_year - year
            if years_old == 0:
                score += 35
                details.append("✓ Published 2024 (cutting edge)")
            elif years_old <= 2:
                score += 30
                details.append(f"✓ Published {year} (very recent)")
            elif years_old <= 5:
                score += 22
                details.append(f"✓ Published {year} (recent)")
            elif years_old <= 10:
                score += 12
                details.append(f"✓ Published {year} (classical)")
            else:
                score += 5
                details.append(f"✓ Published {year} (foundational)")
    except (ValueError, TypeError):
        pass

    # Check for citations (worth 40 points)
    try:
        citations = paper.get('citationCount', 0)
        if not citations:
            citations = paper.get('citation_count', 0)
        citations = int(citations) if citations else 0

        if citations > 100:
            score += 40
            details.append(f"✓ {citations}+ citations (landmark paper)")
        elif citations > 50:
            score += 35
            details.append(f"✓ {citations} citations (highly influential)")
        elif citations > 20:
            score += 28
            details.append(f"✓ {citations} citations (influential)")
        elif citations > 10:
            score += 18
            details.append(f"✓ {citations} citations")
        elif citations > 0:
            score += 8
            details.append(f"✓ {citations} citations")
        else:
            score += 2
            details.append("✓ Uncited (new paper)")
    except (ValueError, TypeError):
        score += 2
        details.append("✓ Citation data unavailable")

    # Cap score at 100
    final_score = min(score, 100)

    return {'score': final_score, 'details': details[:4]}


def extract_consensus_findings(papers: list, contradictions: list) -> dict:
    """Extract common findings across papers (consensus)."""
    if not papers:
        return {'consensus': [], 'agreement_rate': 0}

    total_papers = len(papers)

    # Extract keywords from abstracts - count unique PAPERS mentioning each keyword
    keyword_paper_count = {}

    for paper in papers:
        abstract = str(paper.get('abstract', '')).lower()
        # Extract words > 5 chars
        words_in_abstract = set([w for w in abstract.split() if len(w) > 5])

        # Count each unique keyword only once per paper
        for word in words_in_abstract:
            keyword_paper_count[word] = keyword_paper_count.get(word, 0) + 1

    # Find most common keywords
    if not keyword_paper_count:
        return {'consensus': [], 'agreement_rate': 0}

    sorted_keywords = sorted(keyword_paper_count.items(), key=lambda x: x[1], reverse=True)
    top_10_keywords = sorted_keywords[:10]

    consensus_findings = []
    for keyword, mention_count in top_10_keywords:
        # Ensure mention_count never exceeds total_papers
        mention_count = min(mention_count, total_papers)
        percentage = (mention_count / total_papers) * 100
        percentage = min(percentage, 100.0)  # Cap at 100%

        # Only include if mentioned in 30%+ of papers
        if mention_count >= max(1, total_papers * 0.3):
            consensus_findings.append({
                'finding': keyword.capitalize(),
                'papers_mentioning': mention_count,
                'percentage': round(percentage, 1)
            })

    return {
        'consensus': consensus_findings,
        'agreement_rate': len(consensus_findings) * 10  # Each of 10 findings = 10%
    }


def identify_research_gaps(papers: list, report: str) -> list:
    """Identify potential research gaps from the analysis."""
    if not papers:
        return []

    gaps = []

    # Gap 1: Check paper diversity by year
    years = []
    for p in papers:
        try:
            year = int(p.get('year', 0))
            if year > 0:
                years.append(year)
        except (ValueError, TypeError):
            pass

    if years:
        year_span = max(years) - min(years)
        if year_span < 5:
            gaps.append({
                'gap': 'Limited Temporal Coverage',
                'description': f'Papers span only {year_span} years. Consider researching historical evolution.',
                'priority': 'High'
            })

    # Gap 2: Check author diversity
    all_authors = []
    for paper in papers:
        authors = paper.get('authors', [])
        if isinstance(authors, list):
            author_list = [str(a).strip() for a in authors if a]
        else:
            author_list = [a.strip() for a in str(authors).split(',') if a.strip()]
        all_authors.extend(author_list)

    if all_authors:
        author_freq = Counter(all_authors)
        top_authors = author_freq.most_common(1)
        if top_authors and top_authors[0][1] > max(1, len(papers) * 0.3):
            gaps.append({
                'gap': 'Limited Author Diversity',
                'description': 'Research dominated by few authors. Look for alternative perspectives.',
                'priority': 'Medium'
            })

    # Gap 3: Suggested next steps
    gaps.append({
        'gap': 'Emerging Trends',
        'description': 'Consider exploring recent publications (last 1-2 years) for latest developments.',
        'priority': 'Medium'
    })

    # Gap 4: Methodology coverage
    gaps.append({
        'gap': 'Methodological Diversity',
        'description': 'Explore papers using different research methodologies (quantitative, qualitative, mixed).',
        'priority': 'Low'
    })

    return gaps


def extract_author_network(papers: list) -> dict:
    """Extract author collaboration network."""
    if not papers:
        return {'top_authors': [], 'total_authors': 0}

    authors = {}

    for paper in papers:
        authors_data = paper.get('authors', [])
        if isinstance(authors_data, list):
            paper_authors = [str(a).strip() for a in authors_data if a]
        else:
            paper_authors = [a.strip() for a in str(authors_data).split(',') if a.strip()]

        for author in paper_authors:
            if author not in authors:
                authors[author] = {'papers': 0, 'collaborators': set()}
            authors[author]['papers'] += 1

            # Track collaborations
            for other_author in paper_authors:
                if other_author != author:
                    authors[author]['collaborators'].add(other_author)

    # Sort by paper count
    top_authors = sorted(authors.items(), key=lambda x: x[1]['papers'], reverse=True)[:10]

    return {
        'top_authors': [
            {
                'name': name,
                'papers': data['papers'],
                'collaborators': len(data['collaborators'])
            }
            for name, data in top_authors
        ],
        'total_authors': len(authors)
    }


def build_reading_roadmap(papers: list) -> list:
    """Build suggested reading order from foundational to advanced."""
    if not papers:
        return []

    # Sort by year (older first - foundational)
    sorted_papers = sorted(papers, key=lambda p: int(p.get('year', 0)))

    roadmap = []

    # Foundational papers (oldest)
    foundational = sorted_papers[:max(1, len(sorted_papers)//4)]
    for paper in foundational:
        roadmap.append({
            'paper': paper.get('title', 'Unknown'),
            'url': paper.get('url', ''),
            'category': 'Foundational',
            'recommendation': 'Start here - establishes core concepts',
            'year': paper.get('year')
        })

    # Intermediate papers
    intermediate = sorted_papers[len(foundational):len(foundational)*2]
    for paper in intermediate:
        roadmap.append({
            'paper': paper.get('title', 'Unknown'),
            'url': paper.get('url', ''),
            'category': 'Intermediate',
            'recommendation': 'Build on foundational knowledge',
            'year': paper.get('year')
        })

    # Advanced papers (recent)
    advanced = sorted_papers[-max(1, len(sorted_papers)//4):]
    for paper in advanced:
        roadmap.append({
            'paper': paper.get('title', 'Unknown'),
            'url': paper.get('url', ''),
            'category': 'Advanced',
            'recommendation': 'Latest research and developments',
            'year': paper.get('year')
        })

    return roadmap


def extract_timeline_data(papers: list) -> dict:
    """Extract timeline data for visualization."""
    year_counts = {}

    for paper in papers:
        year = paper.get('year', 'Unknown')
        if year and year != 'Unknown':
            try:
                year = int(year)
                year_counts[year] = year_counts.get(year, 0) + 1
            except (ValueError, TypeError):
                pass

    # Sort by year
    timeline = sorted(year_counts.items()) if year_counts else []

    return {
        'timeline': timeline,
        'total_years': len(timeline),
        'earliest': timeline[0][0] if timeline else None,
        'latest': timeline[-1][0] if timeline else None,
        'peak_year': max(timeline, key=lambda x: x[1])[0] if timeline else None
    }


def find_related_topics(report: str, topic: str) -> list:
    """Suggest related research topics based on report content."""
    # Extract potential related topics from report
    related = []

    topic_keywords = [
        'machine learning', 'deep learning', 'neural networks',
        'artificial intelligence', 'data science', 'nlp',
        'computer vision', 'reinforcement learning',
        'healthcare', 'finance', 'climate', 'education',
        'security', 'privacy', 'optimization'
    ]

    found_keywords = [kw for kw in topic_keywords if kw.lower() in report.lower()]

    for keyword in found_keywords[:5]:
        related.append({
            'topic': keyword,
            'connection': f'Mentioned in research analysis',
            'relevance': 'High'
        })

    return related
