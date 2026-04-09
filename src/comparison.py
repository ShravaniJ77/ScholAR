"""Topic comparison module for ScholAR research data."""


def compare_topics(data_topic1: dict, data_topic2: dict) -> dict:
    """Compare two research topics."""
    papers1 = data_topic1.get('papers', [])
    papers2 = data_topic2.get('papers', [])

    contradictions1 = data_topic1.get('contradictions', [])
    contradictions2 = data_topic2.get('contradictions', [])

    # Extract common keywords from titles and abstracts
    keywords1 = set()
    keywords2 = set()

    for paper in papers1:
        abstract = str(paper.get('abstract', '')).lower()
        title = str(paper.get('title', '')).lower()
        combined = f"{title} {abstract}"
        words = [w for w in combined.split() if len(w) > 5 and w.isalpha()]
        keywords1.update(words[:10])

    for paper in papers2:
        abstract = str(paper.get('abstract', '')).lower()
        title = str(paper.get('title', '')).lower()
        combined = f"{title} {abstract}"
        words = [w for w in combined.split() if len(w) > 5 and w.isalpha()]
        keywords2.update(words[:10])

    common_keywords = keywords1.intersection(keywords2)
    unique_to_1 = keywords1 - keywords2
    unique_to_2 = keywords2 - keywords1

    # Calculate max extent for overlap
    max_keywords = max(len(keywords1), len(keywords2)) if max(len(keywords1), len(keywords2)) > 0 else 1

    return {
        'topic1': data_topic1.get('topic', 'Topic 1'),
        'topic2': data_topic2.get('topic', 'Topic 2'),
        'papers1_count': len(papers1),
        'papers2_count': len(papers2),
        'contradictions1_count': len(contradictions1),
        'contradictions2_count': len(contradictions2),
        'common_keywords': sorted(list(common_keywords))[:10],
        'unique_to_topic1': sorted(list(unique_to_1))[:5],
        'unique_to_topic2': sorted(list(unique_to_2))[:5],
        'overlap_percentage': round(len(common_keywords) / max_keywords * 100, 1)
    }


def find_related_topics_by_keywords(papers: list, n: int = 5) -> list:
    """Find related topics based on paper keywords."""
    keyword_freq = {}

    for paper in papers:
        abstract = str(paper.get('abstract', '')).lower()
        title = str(paper.get('title', '')).lower()
        combined = f"{title} {abstract}"

        # Extract keywords (words > 6 chars, alphabetic only)
        keywords = [w for w in combined.split() if len(w) > 6 and w.isalpha()]
        for kw in keywords:
            keyword_freq[kw] = keyword_freq.get(kw, 0) + 1

    # Get top keywords as related topics
    top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:n]

    return [
        {
            'topic': kw.capitalize(),
            'relevance_score': freq,
            'recommendation': f'Related to research with {freq} paper mentions'
        }
        for kw, freq in top_keywords
    ]

