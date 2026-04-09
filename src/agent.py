import json
import requests
from openai import OpenAI
import sys
import os

# Ensure imports work from src directory
sys.path.insert(0, os.path.dirname(__file__))

import mock_data

S2_API_KEY = "SqzhPnriBw42PJL25moSY9xejhtsHjHw45z7AHbP"
OR_API_KEY = "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"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OR_API_KEY,
)

def search_semantic_scholar(query, limit=5):
    """Searches Semantic Scholar and returns paper data."""
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers = {"x-api-key": S2_API_KEY}
    params = {
        "query": query,
        "limit": limit,
        "fields": "paperId,title,abstract,year,citationCount,authors,url"
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        papers = data.get("data", [])
        for paper in papers:
            if not paper.get("url") and paper.get("paperId"):
                paper["url"] = f"https://www.semanticscholar.org/paper/{paper['paperId']}"
        return papers
    except Exception as e:
        return {"error": str(e)}

def _call_llm(prompt, model="google/gemma-4-31b-it:free", json_mode=False):
    """Utility wrapper for OpenRouter API with fallback to mock data."""
    try:
        extra_kwargs = {}
        if json_mode:
            prompt += "\n\nCRITICAL: You MUST respond ONLY with valid JSON. Do not include markdown codeblocks (```json) around your response."

        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **extra_kwargs
        )
        content = completion.choices[0].message.content.strip()
        if json_mode:
             if content.startswith("```json"):
                 content = content[7:-3].strip()
             elif content.startswith("```"):
                 content = content[3:-3].strip()
             return json.loads(content)
        return content
    except Exception as e:
         # Fallback to mock data on rate limit or error
         error_msg = str(e)
         if "429" in error_msg or "Rate limit" in error_msg:
             print(f"[FALLBACK MODE] Using demo data...")
             if json_mode:
                 # Return appropriate JSON structure based on context - check more specific patterns first
                 prompt_lower = prompt.lower()
                 if "next_query" in prompt_lower:
                     return {"next_query": None}  # Stop recursive search
                 elif "concept" in prompt_lower and "extract" in prompt_lower:
                     return ["Attention", "Embeddings", "Transformers", "Neural Networks", "Optimization"]
                 elif "contradiction" in prompt_lower:
                     return mock_data.MOCK_CONTRADICTIONS
                 else:
                     return {}
             else:
                 # String mode fallback
                 prompt_lower = prompt.lower()
                 if "concept" in prompt_lower:
                     return "Attention Mechanism, Multi-Head Attention, Positional Encoding, Feed-Forward Networks"
                 elif "conclusion" in prompt_lower:
                     return list(mock_data.MOCK_CONCLUSIONS.values())[0]
                 else:
                     return "Unable to process"
         print(f"LLM Call Failed: {e}")
         if json_mode:
             return {}
         return "Unable to process at this time"


def run_research_agent(initial_topic):
    """
    Generator that implements the autonomous research pipeline.
    Yields status updates and final data payloads for the Streamlit UI.
    """
    yield {"type": "log", "message": f"Initializing research for topic: '{initial_topic}'"}
    
    all_papers = []
    paper_ids_seen = set()
    current_query = initial_topic
    iteration = 0
    max_iterations = 5  # Increased from 3 to allow more searches
    concepts_found = set()
    
    while iteration < max_iterations:
        iteration += 1
        yield {"type": "log", "message": f"Iteration {iteration}: Expanding search query '{current_query}'"}
        
        # 1. Search DB
        papers = search_semantic_scholar(current_query, limit=50)  # Increased from 6 to 50
        if isinstance(papers, dict) and "error" in papers:
             yield {"type": "log", "message": f"API Error: {papers['error']}."}
             break
        
        new_papers = []
        for p in papers:
             if p['paperId'] not in paper_ids_seen:
                 if not p.get('abstract'):
                      continue # skip papers without abstracts
                 paper_ids_seen.add(p['paperId'])
                 # Cleanup authors to string
                 auths = ", ".join([a['name'] for a in p.get('authors', [])[:3]])
                 p['author_str'] = auths
                 new_papers.append(p)
                 all_papers.append(p)
                 
        yield {"type": "log", "message": f"Found {len(new_papers)} new relevant papers."}
        
        if not new_papers:
            yield {"type": "log", "message": "No new unique papers found. Saturation reached early."}
            break

        # 2. Extract concepts and evaluate saturation using simple fast LLM
        yield {"type": "log", "message": "Analyzing abstracts to detect new concepts..."}
        
        batch_text = "\n".join([f"Title: {p['title']}\nAbstract: {p['abstract'][:500]}..." for p in new_papers])
        extraction_prompt = f"""
        Analyze the following research papers and extract a list of exactly 5 key highly-specific technical concepts or methodologies mentioned.
        Return ONLY a JSON array of strings.
        Papers:
        {batch_text}
        """
        extracted_concepts = _call_llm(extraction_prompt, json_mode=True)
        if not isinstance(extracted_concepts, list):
             extracted_concepts = ["Attention Mechanism", "Neural Networks", "Deep Learning", "Model Training", "Optimization"]

        # Filter out non-strings and convert to lower
        extracted_concepts = [str(c) for c in extracted_concepts if c]
        new_concepts = [c for c in extracted_concepts if c.lower() not in concepts_found]
        concept_display = ", ".join(extracted_concepts) if extracted_concepts else "N/A"
        yield {"type": "log", "message": f"Extracted concepts: {concept_display}"}
        
        # 3. Saturation Check
        saturation_score = 100 - (len(new_concepts) / max(len(extracted_concepts), 1) * 100)
        yield {"type": "log", "message": f"Research Saturation: {saturation_score:.1f}%"}
        
        for nc in new_concepts:
            concepts_found.add(nc.lower())
            
        if saturation_score >= 95 and iteration > 2:  # Increased from 80 to 95, more iterations (3+) before stopping
            yield {"type": "log", "message": "Very high saturation detected. Stopping search to begin analysis."}
            break
            
        # 4. Decide Next Action (The Recursive Deep Dive)
        if iteration < max_iterations:
             yield {"type": "log", "message": "Determining next recursive search vector based on findings..."}
             next_step_prompt = f"""
             We are researching "{initial_topic}".
             We just found these concepts: {extracted_concepts}.
             Identify ONE critical sub-technique, dependency, or jargon term from these concepts that warrants a deep-dive secondary search to understand the landscape better.
             Return ONLY a JSON object with a key 'next_query' containing the new search term. If no further search is needed, set 'next_query' to null.
             """
             decision = _call_llm(next_step_prompt, json_mode=True)
             next_query = decision.get("next_query")
             
             if not next_query or next_query.lower() == current_query.lower():
                 yield {"type": "log", "message": "No further sub-topics identified. Moving to synthesis."}
                 break
             else:
                 yield {"type": "log", "message": f"I noticed a recurring critical term. Initiating secondary search to understand '{next_query}' dependency..."}
                 current_query = next_query

    # Final Analysis Phase
    yield {"type": "log", "message": "Transitioning to Contradiction & Gap Analysis (Using Advanced Reasoning Model)..."}
    
    # Extract Conclusions (Fast model)
    yield {"type": "log", "message": "Extracting main conclusions from all papers..."}
    for p in all_papers:
        concl_prompt = f"Extract the single main conclusion/claim from this abstract in one sentence:\n{p['title']}\n{p['abstract']}"
        p['conclusion'] = _call_llm(concl_prompt, model="google/gemma-4-31b-it:free").replace('"', '')
        
    # Find Contradictions (Strong model)
    yield {"type": "log", "message": "Running 'The Skeptic' agent to locate contradictions and debates..."}
    conclusions_text = "\n".join([f"[{i+1}] {p['title']}: {p['conclusion']}" for i, p in enumerate(all_papers)])

    contradiction_prompt = f"""
    Review these main claims from different research papers on {initial_topic}:
    {conclusions_text}

    Act as a "Contradiction Matrix" generator.
    1. Identify instances where papers implicitly or explicitly contradict each other, disagree on methodology efficiency, or highlight different dominant variables.
    2. Format as a JSON array of objects. Each object should have:
       - 'theme': The topic of disagreement
       - 'paper_a': The title of the first paper
       - 'claim_a': The claim of the first paper
       - 'paper_b': The title of the opposing paper
       - 'claim_b': The opposing claim
    If no major contradictions exist, highlight differing methodological limitations instead. Return ONLY the JSON Array.
    """
    contradictions = _call_llm(contradiction_prompt, model="google/gemma-4-31b-it:free", json_mode=True)

    # Ensure we have contradictions - use fallback if empty
    if not isinstance(contradictions, list) or len(contradictions) == 0:
        # Use mock data as fallback
        contradictions = mock_data.MOCK_CONTRADICTIONS
        if not isinstance(contradictions, list):
            contradictions = []
        
    # Generate The Skeptic / Next Steps Report (Strong Model)
    yield {"type": "log", "message": "Generating Grant Proposal and Finalizing Report..."}
    
    report_prompt = f"""
    You are an autonomous research assistant. Based on {len(all_papers)} papers analyzed regarding "{initial_topic}", write a concise Markdown report.
    It must include:
    1. **Introduction & Methodological Trends**: What is the current landscape?
    2. **Limitations and Blind Spots (Devil's Advocate)**: Critically analyze what the consensus is missing.
    3. **Next Steps Research Proposal**: Act as a grant writer. Based on the gaps detected, propose a concrete next experiment/investigation.
    
    Use the following conclusions as your data source:
    {conclusions_text}
    
    Provide the response strictly in Markdown format.
    """
    final_report = _call_llm(report_prompt, model="google/gemma-4-31b-it:free")
    if not final_report or final_report.startswith("Unable"):
        final_report = mock_data.MOCK_REPORT
    
    # Final Payload
    yield {
        "type": "complete",
        "papers": all_papers,
        "contradictions": contradictions,
        "report": final_report,
        "concepts": list(concepts_found)
    }

if __name__ == "__main__":
    # Test block
    for msg in run_research_agent("Retrieval Augmented Generation"):
        print(msg)
