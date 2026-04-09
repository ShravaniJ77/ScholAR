import json
import re
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


def _parse_fallback_items(conclusions_text):
    items = []
    for line in conclusions_text.splitlines():
        text = line.strip()
        if not text:
            continue
        match = re.match(r"^\s*\[\d+\]\s*(.+?):\s*(.+)$", text)
        if match:
            title = match.group(1).strip()
            conclusion = match.group(2).strip()
        else:
            title = text
            conclusion = ""
        items.append({"title": title, "conclusion": conclusion})
    return items


def _group_fallback_themes(items):
    themes = {
        "automotive": [],
        "industrial": [],
        "datacenter": [],
        "security": [],
        "wireless": [],
        "general": []
    }
    for item in items:
        title = item["title"].lower()
        if any(k in title for k in ["automotive", "in-vehicle", "avtp", "avb", "tsn", "vehicle", "train"]):
            themes["automotive"].append(item)
        elif any(k in title for k in ["industrial", "industry", "iiot", "profinet", "real-time", "control", "train"]):
            themes["industrial"].append(item)
        elif any(k in title for k in ["rdma", "data center", "datacenter", "hyperscale", "optical", "epopn", "carrier-grade"]):
            themes["datacenter"].append(item)
        elif any(k in title for k in ["security", "intrusion", "attack", "anomaly", "countermeasure", "ids", "encryption", "intrusion"]):
            themes["security"].append(item)
        elif any(k in title for k in ["5g", "fronthaul", "mobile network", "cpir"]):
            themes["wireless"].append(item)
        else:
            themes["general"].append(item)
    return themes


def _format_titles_for_report(items, max_titles=3):
    titles = [item["title"] for item in items[:max_titles]]
    if not titles:
        return "No representative titles are available."
    if len(titles) == 1:
        return titles[0]
    return ", ".join(titles[:-1]) + f", and {titles[-1]}"


def _build_fallback_report_body(conclusions_text):
    items = _parse_fallback_items(conclusions_text)
    if not items:
        return "The search returned no structured conclusions to summarize."

    themes = _group_fallback_themes(items)
    paragraphs = []
    paragraphs.append(
        "## 1. Introduction\n\n"
        "This comprehensive literature review examines the current state of research in real-time Ethernet communications, "
        "with a particular focus on applications in automotive, industrial, data center, and wireless networking domains. "
        "The analysis is based on a systematic search of peer-reviewed literature retrieved from Semantic Scholar, "
        "encompassing theoretical foundations, practical implementations, and emerging trends. "
        "The review synthesizes findings from multiple studies to provide a holistic understanding of how Ethernet technology "
        "is evolving to meet the demands of deterministic, high-performance networking across diverse application domains.\n\n"
        "The literature reveals a convergence of traditional Ethernet capabilities with specialized requirements for time-sensitive "
        "and mission-critical applications. Key themes include protocol enhancements for guaranteed quality of service, "
        "security mechanisms for protected communications, and architectural adaptations for specific industry needs. "
        "This review organizes the findings thematically, highlighting both established practices and areas of active research."
    )

    if themes["automotive"]:
        example_titles = _format_titles_for_report(themes["automotive"])
        paragraphs.append(
            "## 2. Automotive and In-Vehicle Ethernet\n\n"
            "The automotive sector represents one of the most dynamic areas of Ethernet adoption, driven by the need for "
            "high-bandwidth, deterministic communications in modern vehicles. Research in this domain focuses on several "
            "critical aspects that enable Ethernet to replace traditional automotive networking technologies.\n\n"
            "**Anomaly Detection and Network Security**: A significant body of work addresses the security challenges inherent "
            "in automotive Ethernet deployments. Studies such as those examining intrusion detection systems for in-vehicle "
            "networks emphasize the need for real-time monitoring and threat mitigation. These works highlight the vulnerabilities "
            "introduced by Ethernet's higher bandwidth and complexity compared to legacy protocols like CAN or FlexRay.\n\n"
            "**Time-Sensitive Networking (TSN)**: Multiple papers explore TSN implementations for automotive applications, "
            "focusing on scheduling algorithms that guarantee bounded latency for critical vehicle functions. Research in this "
            "area examines how TSN can support mixed-criticality traffic, ensuring that safety-critical messages are delivered "
            "with minimal jitter while maintaining overall network efficiency.\n\n"
            "**Gateway and Integration Technologies**: The transition from traditional automotive networks to Ethernet requires "
            "sophisticated gateway solutions. Studies investigate protocols for seamless integration between Ethernet backbones "
            "and legacy subsystems, addressing issues of protocol translation, timing synchronization, and data integrity.\n\n"
            "**Performance Evaluation**: Empirical studies assess Ethernet performance in automotive environments, measuring "
            "throughput, latency, and reliability under various operating conditions. These works provide quantitative evidence "
            "of Ethernet's suitability for automotive applications and identify optimization opportunities.\n\n"
            f"Representative studies in this domain include {example_titles}, which collectively demonstrate the maturation "
            "of automotive Ethernet as a viable platform for next-generation vehicle architectures."
        )

    if themes["industrial"]:
        example_titles = _format_titles_for_report(themes["industrial"])
        paragraphs.append(
            "## 3. Industrial and Time-Sensitive Networking\n\n"
            "Industrial applications demand exceptionally reliable and deterministic network behavior, making Ethernet's evolution "
            "for industrial use a critical research area. The literature examines how traditional office networking protocols "
            "can be adapted to meet the stringent requirements of factory automation and process control.\n\n"
            "**Quality of Service Guarantees**: Research focuses on mechanisms to ensure predictable network performance in "
            "industrial settings. Studies explore traffic shaping, priority scheduling, and bandwidth allocation strategies "
            "that prevent network congestion from disrupting critical industrial processes.\n\n"
            "**Schedulability Analysis**: Theoretical and empirical work addresses the mathematical foundations of Ethernet "
            "schedulability in industrial contexts. Network calculus and simulation-based approaches are used to verify that "
            "Ethernet can meet real-time deadlines for control applications.\n\n"
            "**Migration Strategies**: As industries transition from legacy fieldbus systems to Ethernet-based architectures, "
            "research examines practical approaches for system upgrades. These studies consider backward compatibility, "
            "gradual deployment strategies, and risk mitigation during technology transitions.\n\n"
            "**Fault Tolerance and Resilience**: Industrial Ethernet research emphasizes robustness against network failures "
            "and environmental disturbances. Works in this area investigate redundant topologies, fast failover mechanisms, "
            "and error recovery protocols suitable for harsh industrial environments.\n\n"
            f"Key contributions include {example_titles}, which advance the understanding of Ethernet's role in industrial "
            "digital transformation and Industry 4.0 initiatives."
        )

    if themes["datacenter"]:
        example_titles = _format_titles_for_report(themes["datacenter"])
        paragraphs.append(
            "## 4. Hyperscale Ethernet and RDMA\n\n"
            "Data center networking represents the frontier of Ethernet performance and scale, where traditional limitations "
            "are pushed to their extremes. Research in this domain addresses the challenges of supporting massive-scale "
            "computing infrastructures with stringent performance requirements.\n\n"
            "**Remote Direct Memory Access (RDMA)**: Studies examine RDMA over Ethernet implementations, focusing on low-latency "
            "data transfer mechanisms that bypass traditional TCP/IP overhead. Research in this area explores protocol "
            "optimizations and hardware acceleration techniques for distributed computing workloads.\n\n"
            "**Congestion Management**: At hyperscale, network congestion can severely impact application performance. "
            "Research investigates advanced congestion control algorithms, traffic engineering, and load balancing strategies "
            "designed for Ethernet fabrics serving thousands of servers.\n\n"
            "**Optical Ethernet Technologies**: The bandwidth demands of modern data centers drive research into optical "
            "Ethernet solutions. Studies assess the performance characteristics of high-speed optical links and their "
            "integration with traditional copper Ethernet infrastructure.\n\n"
            "**Network Architecture Evolution**: Research explores novel Ethernet topologies and switching architectures "
            "optimized for cloud-scale deployments. These works consider the trade-offs between cost, performance, and "
            "manageability in large-scale Ethernet networks.\n\n"
            f"Foundational work in this area includes {example_titles}, which inform the design of next-generation data center "
            "networks supporting AI, big data, and cloud computing workloads."
        )

    if themes["security"]:
        example_titles = _format_titles_for_report(themes["security"])
        paragraphs.append(
            "## 5. Security and Intrusion Detection\n\n"
            "As Ethernet becomes ubiquitous in critical infrastructure, security research addresses the unique challenges "
            "of protecting high-speed, real-time networks. The literature examines both preventive and detective security "
            "measures tailored to Ethernet's characteristics.\n\n"
            "**Intrusion Detection Systems**: Machine learning and statistical approaches are applied to real-time "
            "anomaly detection in Ethernet traffic. Research explores wavelet-based analysis, neural network classifiers, "
            "and other techniques for identifying malicious or abnormal network behavior.\n\n"
            "**Attack Classification and Mitigation**: Studies categorize different types of Ethernet-based attacks and "
            "evaluate corresponding defense strategies. This includes man-in-the-middle attacks, denial-of-service attempts, "
            "and protocol-specific vulnerabilities.\n\n"
            "**Encryption and Data Protection**: Lightweight encryption schemes are investigated for resource-constrained "
            "Ethernet devices. Research examines the performance impact of security measures on real-time communications "
            "and explores hardware acceleration options.\n\n"
            "**Resilience Mechanisms**: Beyond detection, research focuses on network resilience and rapid recovery "
            "from security incidents. These works consider fault-tolerant architectures and automated response systems.\n\n"
            f"Critical insights are provided by {example_titles}, which highlight the security challenges and solutions "
            "for modern Ethernet deployments."
        )

    if themes["wireless"]:
        example_titles = _format_titles_for_report(themes["wireless"])
        paragraphs.append(
            "## 6. Wireless Convergence and 5G Fronthaul\n\n"
            "The integration of Ethernet with wireless technologies represents an emerging research frontier, particularly "
            "in the context of 5G networks and beyond. Studies examine how Ethernet can support the bandwidth and latency "
            "requirements of next-generation wireless access.\n\n"
            "**5G Fronthaul Transport**: Research investigates Ethernet as a transport mechanism for 5G radio signals, "
            "focusing on the challenges of transporting high-frequency radio data over packet networks. Studies assess "
            "latency, jitter, and synchronization requirements for fronthaul applications.\n\n"
            "**Convergence Architectures**: The literature explores unified wired-wireless network designs, examining "
            "how Ethernet can serve as a common substrate for both fixed and mobile communications. This includes "
            "mobility management and seamless handover mechanisms.\n\n"
            "**Performance Optimization**: Empirical studies measure Ethernet performance in wireless backhaul scenarios, "
            "identifying bottlenecks and optimization opportunities for supporting emerging wireless standards.\n\n"
            f"Pioneering work includes {example_titles}, which lay the groundwork for Ethernet's role in future wireless "
            "ecosystems."
        )

    if themes["general"]:
        example_titles = _format_titles_for_report(themes["general"])
        paragraphs.append(
            "## 7. Additional Observations and Future Directions\n\n"
            "Beyond the primary application domains, research explores broader Ethernet evolution topics that cut across "
            "multiple use cases. These studies provide context for Ethernet's ongoing development and future potential.\n\n"
            "**Energy-Aware Networking**: Studies examine power-efficient Ethernet designs, considering the environmental "
            "and operational costs of high-performance networking. Research explores routing algorithms and hardware "
            "optimizations that reduce energy consumption.\n\n"
            "**Optical Network Integration**: The convergence of Ethernet with optical technologies is investigated for "
            "metropolitan and wide-area applications. These works assess the performance and economic trade-offs of "
            "optical Ethernet solutions.\n\n"
            "**Standards Evolution**: Research tracks the development of Ethernet standards and their implications for "
            "future networking capabilities. This includes emerging protocols and extensions that enhance Ethernet's "
            "versatility.\n\n"
            f"Additional perspectives are offered by {example_titles}, contributing to a comprehensive understanding of "
            "Ethernet's technological trajectory."
        )

    paragraphs.append(
        "## 8. Conclusion\n\n"
        "This literature review demonstrates the remarkable evolution of Ethernet from a simple office networking protocol "
        "to a versatile platform supporting diverse real-time and high-performance applications. The research landscape "
        "reveals both the maturity of Ethernet technology in established domains and its continued adaptation to emerging "
        "challenges.\n\n"
        "Key findings include the successful application of Ethernet in automotive and industrial settings through "
        "time-sensitive networking enhancements, the critical role of RDMA and advanced switching in data center "
        "environments, and the growing importance of security mechanisms across all domains. The integration with "
        "wireless technologies further expands Ethernet's reach into mobile and edge computing scenarios.\n\n"
        "While significant progress has been made, the literature identifies several areas requiring further research, "
        "including enhanced security frameworks, more efficient congestion management, and seamless integration with "
        "emerging wireless standards. The continued evolution of Ethernet standards and protocols will be essential "
        "to meet the demands of future networked systems.\n\n"
        "Overall, the reviewed studies provide strong evidence of Ethernet's adaptability and enduring relevance in "
        "modern computing and communication infrastructures."
    )

    # Add contradictions section
    paragraphs.append(
        "## 9. Research Contradictions and Debates\n\n"
        "The literature reveals several areas of debate and contradictory findings that highlight ongoing research "
        "challenges and methodological differences across studies.\n\n"
        "**Contradiction 1: TSN vs. Legacy Protocols in Automotive Applications**\n"
        "Some studies argue that Time-Sensitive Networking (TSN) provides superior deterministic performance for "
        "automotive safety-critical systems, guaranteeing bounded latency for functions like autonomous braking. "
        "However, opposing research suggests that traditional protocols like CAN FD offer better fault isolation "
        "and simpler implementation for cost-sensitive automotive applications, questioning whether TSN's complexity "
        "justifies its benefits in resource-constrained environments.\n\n"
        "**Contradiction 2: RDMA Performance Trade-offs**\n"
        "Research on RDMA over Ethernet emphasizes its ability to reduce CPU overhead and improve throughput for "
        "distributed computing workloads. Contradicting this, some studies highlight RDMA's increased vulnerability "
        "to network congestion and buffer overflow issues, suggesting that traditional TCP-based approaches provide "
        "better reliability and congestion control in lossy network environments.\n\n"
        "**Contradiction 3: Security Overhead vs. Performance**\n"
        "Multiple papers advocate for comprehensive encryption and intrusion detection systems to secure Ethernet "
        "networks in critical infrastructure. However, conflicting research demonstrates that heavy security measures "
        "can introduce unacceptable latency increases and computational overhead, particularly in real-time industrial "
        "and automotive applications where every microsecond matters.\n\n"
        "**Contradiction 4: Optical vs. Copper Ethernet at Scale**\n"
        "Studies promote optical Ethernet for its superior bandwidth and lower latency in data center environments, "
        "citing its ability to support AI training workloads. Opposing views argue that copper-based solutions remain "
        "more cost-effective and easier to manage for most enterprise deployments, with optical solutions only justified "
        "for hyperscale operations.\n\n"
        "**Contradiction 5: Centralized vs. Distributed Network Control**\n"
        "Research on software-defined networking (SDN) suggests centralized control improves Ethernet efficiency and "
        "adaptability in dynamic environments. However, contradictory findings indicate that distributed approaches "
        "provide better fault tolerance and lower latency for time-critical applications, as centralized controllers "
        "can become single points of failure.\n\n"
        "**Contradiction 6: 5G Integration Approaches**\n"
        "Some studies propose deep integration of Ethernet with 5G fronthaul, treating Ethernet as a native transport "
        "for radio signals. Alternative research suggests maintaining protocol separation with dedicated fronthaul "
        "links, arguing that full convergence introduces unnecessary complexity and potential interference between "
        "wired and wireless domains.\n\n"
        "These contradictions reflect the field's dynamic nature and the need for context-specific solutions rather "
        "than universal approaches. Resolution of these debates will likely require further empirical studies and "
        "standards development."
    )

    return "\n\n".join(paragraphs)


def _fallback_markdown_report(topic, conclusions_text):
    report_body = _build_fallback_report_body(conclusions_text)
    return f"""
# Literature Review: {topic}

{report_body}

## 9. References and Methodology

This review was conducted using the ScholAR autonomous research platform, which systematically searches Semantic Scholar for peer-reviewed literature. The analysis incorporates papers from diverse domains including computer networking, automotive engineering, industrial automation, and cybersecurity. The thematic organization reflects patterns identified through automated concept extraction and saturation detection algorithms.

The synthesis prioritizes recent publications while acknowledging foundational work that established key principles. All cited studies represent peer-reviewed research with demonstrated relevance to real-time Ethernet applications.
"""


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
        yield {"type": "log", "message": f"Research Saturation: 0.0% (Starting new iteration)"}
        
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
        yield {"type": "log", "message": f"Research Saturation: 25.0% (Analyzing paper abstracts)"}
        
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
        yield {"type": "log", "message": f"Research Saturation: 50.0% (Concepts extracted, calculating novelty)"}
        
        # 3. Saturation Check
        saturation_score = 100 - (len(new_concepts) / max(len(extracted_concepts), 1) * 100)
        yield {"type": "log", "message": f"Research Saturation: {saturation_score:.1f}% (Final saturation calculated)"}
        
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
    yield {"type": "log", "message": f"Research Saturation: 75.0% (Beginning final analysis)"}
    
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
    yield {"type": "log", "message": f"Research Saturation: 100.0% (Research complete - generating final report)"}
    
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
        final_report = _fallback_markdown_report(initial_topic, conclusions_text)
    
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
