"""Multi-format export module for ScholAR research data."""

import json
import csv
from io import StringIO, BytesIO
from datetime import datetime


def export_to_bibtex(papers: list) -> str:
    """Export papers to BibTeX format."""
    bibtex_entries = []

    for idx, paper in enumerate(papers):
        title = paper.get('title', 'Unknown').replace('"', '\\"')
        authors = paper.get('author_str', 'Unknown')
        year = paper.get('year', 'Unknown')
        abstract = paper.get('abstract', '')

        # Generate citation key from title
        title_words = title.split()[:3]
        cite_key = f"{year}_{'-'.join([w[:3] for w in title_words])}"

        bibtex = f"""@article{{{cite_key},
  title = {{{title}}},
  author = {{{authors}}},
  year = {{{year}}},
  abstract = {{{abstract}}}
}}"""
        bibtex_entries.append(bibtex)

    return "\n\n".join(bibtex_entries)


def export_to_markdown(topic: str, papers: list, contradictions: list, report: str) -> str:
    """Export complete research to Markdown format."""
    md = []

    md.append(f"# Literature Review: {topic}\n")
    md.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    md.append("## Executive Summary\n")
    md.append(f"- **Papers Reviewed:** {len(papers)}\n")
    md.append(f"- **Contradictions Found:** {len(contradictions)}\n")
    md.append(f"- **Topic:** {topic}\n\n")

    md.append("## Research Analysis\n")
    md.append(report)
    md.append("\n\n")

    md.append("## Papers\n\n")
    for idx, paper in enumerate(papers, 1):
        md.append(f"### {idx}. {paper.get('title', 'N/A')}\n")
        md.append(f"- **Authors:** {paper.get('author_str', 'N/A')}\n")
        md.append(f"- **Year:** {paper.get('year', 'N/A')}\n")
        md.append(f"- **Abstract:** {paper.get('abstract', 'N/A')}\n\n")

    if contradictions:
        md.append("## Contradictions\n\n")
        for idx, contra in enumerate(contradictions, 1):
            md.append(f"### {idx}. {contra.get('theme', 'N/A')}\n")
            md.append(f"- **Paper A:** {contra.get('paper_a', 'N/A')}\n")
            md.append(f"  - Claim: {contra.get('claim_a', 'N/A')}\n")
            md.append(f"- **Paper B:** {contra.get('paper_b', 'N/A')}\n")
            md.append(f"  - Claim: {contra.get('claim_b', 'N/A')}\n\n")

    return "".join(md)


def export_to_csv(papers: list) -> str:
    """Export papers to CSV format."""
    if not papers:
        return ""

    output = StringIO()
    fieldnames = ['#', 'Title', 'Authors', 'Year', 'Abstract']
    writer = csv.DictWriter(output, fieldnames=fieldnames)

    writer.writeheader()
    for idx, paper in enumerate(papers, 1):
        writer.writerow({
            '#': idx,
            'Title': paper.get('title', 'N/A'),
            'Authors': paper.get('author_str', 'N/A'),
            'Year': paper.get('year', 'N/A'),
            'Abstract': paper.get('abstract', 'N/A')[:100] + '...' if paper.get('abstract') else 'N/A'
        })

    return output.getvalue()


def export_to_json(topic: str, papers: list, contradictions: list, report: str) -> str:
    """Export complete research to JSON format."""
    data = {
        'topic': topic,
        'timestamp': datetime.now().isoformat(),
        'statistics': {
            'papers_count': len(papers),
            'contradictions_count': len(contradictions)
        },
        'report': report,
        'papers': papers,
        'contradictions': contradictions
    }

    return json.dumps(data, indent=2)


def export_to_ris(papers: list) -> str:
    """Export papers to RIS format (for Zotero/Mendeley)."""
    ris_entries = []

    for paper in papers:
        ris = []
        ris.append("TY  - JOUR")
        ris.append(f"TI  - {paper.get('title', 'Unknown')}")
        ris.append(f"AU  - {paper.get('author_str', 'Unknown')}")
        ris.append(f"PY  - {paper.get('year', 'Unknown')}")
        ris.append(f"AB  - {paper.get('abstract', '')}")
        ris.append("ER  - \n")
        ris_entries.append("\n".join(ris))

    return "".join(ris_entries)


def export_to_html(topic: str, papers: list, contradictions: list, report: str) -> str:
    """Export research to HTML format."""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Literature Review: {topic}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 40px auto; line-height: 1.6; }}
        h1 {{ color: #333; border-bottom: 3px solid #7b2fff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .stats {{ background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .paper {{ background: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #7b2fff; }}
        .contradiction {{ background: #ffe6e6; padding: 15px; margin: 10px 0; border-left: 4px solid #ff0000; }}
    </style>
</head>
<body>
    <h1>Literature Review: {topic}</h1>
    <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <div class="stats">
        <p><strong>Papers:</strong> {len(papers)} | <strong>Contradictions:</strong> {len(contradictions)}</p>
    </div>

    <h2>Analysis</h2>
    <p>{report.replace(chr(10), '<br>')}</p>

    <h2>Papers Reviewed</h2>
    {"".join([f'''
    <div class="paper">
        <h3>{paper.get('title', 'Unknown')}</h3>
        <p><strong>Authors:</strong> {paper.get('author_str', 'Unknown')}</p>
        <p><strong>Year:</strong> {paper.get('year', 'Unknown')}</p>
        <p><strong>Abstract:</strong> {paper.get('abstract', 'N/A')[:200]}...</p>
    </div>
    ''' for paper in papers])}

</body>
</html>"""

    return html
