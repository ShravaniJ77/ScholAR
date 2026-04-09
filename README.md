# 📚 ScholAR - Autonomous Research Discovery Platform

ScholAR is an intelligent literature review system that automatically searches, analyzes, and synthesizes academic research papers using AI and autonomous agents. It transforms scattered research into comprehensive, actionable insights.

## 🌟 Key Features

### 1. **Autonomous Paper Discovery**
- Searches 100M+ papers via **Semantic Scholar API**
- Recursive search with saturation detection
- Analyzes up to 50 papers per query
- Intelligent concept extraction

### 2. **Research Caching & History**
- **Instant search recall**: Search topic X, then Y, then X again = instant cache hit
- Local SQLite database tracks all searches
- Never re-search the same topic unprompted
- **"Force New"** button to override cache when needed

### 3. **Advanced Analysis**

#### 📊 Dashboard
- Paper quality scoring (🟢🟡🔴) based on:
  - Abstract comprehensiveness (0-25 pts)
  - Author collaboration (0-20 pts)
  - Publication recency (0-35 pts)
  - Citation impact (0-40 pts)
- Sort by quality, publication year
- Publication timeline visualization
- Research completeness status

#### 🕸️ Knowledge Graph
- Interactive concept visualization
- Click nodes to explore relationships
- Paper-to-concept mapping
- Hierarchical concept clustering

#### 🤝 Contradictions
- AI-detected research conflicts
- Grouped by research theme
- Shows opposing claims from different papers
- Highlights areas of scientific disagreement

#### 📑 Full Report
- Complete markdown analysis
- AI-synthesized findings from all papers
- Professional formatting
- **Downloadable as PDF** with:
  - Executive summary
  - Complete literature analysis
  - All papers reviewed
  - Contradictions documented
  - Methodology & conclusions

#### 📚 Sources
- Complete paper list with:
  - Title, authors, year, abstract
  - Citation count indicators
  - Bookmark important papers (⭐)
  - Filter by bookmarked/year range
  - Sort by title, year, or citations

#### 🔍 Research Gaps
- Identifies missing research areas:
  - Temporal coverage gaps
  - Author diversity analysis
  - Emerging trends to explore
  - Methodological gaps
- Prioritized by importance

#### 📈 Timeline
- Publication frequency by year
- Earliest/latest/peak paper year
- Research evolution tracking
- Interactive bar chart

#### 👥 Authors
- Top 10 most published researchers
- Co-author collaboration networks
- Influence scores
- Author productivity metrics

#### 🛣️ Reading Path
- Suggested reading order:
  - **Foundational**: Older seminal works
  - **Intermediate**: Development of field
  - **Advanced**: Latest cutting-edge research
- Personalized learning sequence

#### 📤 Export Center
- **Multiple export formats:**
  - 📄 **PDF**: Complete literature review
  - 📋 **CSV**: Spreadsheet analysis
  - 📝 **Markdown**: Wiki/documentation
  - 📦 **JSON**: Programmatic use
  - 🏷️ **BibTeX**: LaTeX citations
  - 📚 **RIS**: Mendeley/Zotero import
  - 🌐 **HTML**: Web viewing

#### 💾 Saved Research
- View all previous research
- Search history browser
- Load cached research
- Delete old searches
- Storage size management

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone <repo-url>
cd scholar

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
```

### Configuration

**Environment Variables** (.env):
```
OPENROUTER_API_KEY=your_key_here
SEMANTIC_SCHOLAR_API=automatic
STORAGE_DIR=scholarpython_research
```

### Running ScholAR

**Option 1: Auto-detect port (recommended)**
```bash
python launch.py
```
Automatically finds available port (8501-8510)

**Option 2: Fixed port**
```bash
streamlit run app/streamlit_app.py --server.port 8501
```

**Option 3: Windows batch file**
```bash
run_updated.bat
```

---

## 📖 How to Use

### Basic Workflow

1. **Enter Research Topic**
   - Type your topic in the sidebar (e.g., "Federated Learning", "Blockchain Security")

2. **Start Research**
   - Click **🚀 Start Research** button
   - System checks cache first
   - If new topic: AI agent autonomously searches and analyzes papers
   - Results persist in local storage

3. **Explore Results**
   - Review papers in **Sources** tab
   - Check contradictions in **Contradictions** tab
   - Read AI synthesis in **Full Report** tab
   - See author network in **Authors** tab

4. **Export & Share**
   - Download complete PDF report
   - Export to BibTeX for LaTeX
   - Share as Markdown or HTML
   - Use JSON for programmatic access

### Pro Tips

- **Cache Hits**: Search same topic later = instant results (no re-search)
- **Force New**: Click "🔄 Force New" to override cache
- **Bookmarks**: Star important papers in Sources tab for quick reference
- **Timeline**: Check publication trends to understand field evolution
- **Gaps**: Review "Research Gaps" for future research directions

---

## 🏗️ Architecture

```
ScholAR/
├── app/
│   └── streamlit_app.py          # Main UI with 11 tabs
├── src/
│   ├── agent.py                  # Autonomous research agent
│   ├── storage.py                # SQLite local storage
│   ├── analysis.py               # Paper quality, gaps, timeline
│   ├── export.py                 # Multi-format exports
│   ├── pdf_generator.py          # PDF generation (ReportLab)
│   └── semantic_scholar.py       # Paper search API
├── scholarpython_research/       # Local data storage
│   ├── research_history.db       # SQLite database
│   └── data/                     # Per-search folders
├── launch.py                     # Port detection launcher
└── requirements.txt              # Python dependencies
```

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit (Python) |
| **Backend** | Python 3.8+ |
| **Database** | SQLite (local) |
| **LLM** | OpenRouter (Google Gemma 4) |
| **Paper Search** | Semantic Scholar API |
| **PDF Generation** | ReportLab |
| **Graphs** | NetworkX, Plotly |
| **Data Format** | JSON, CSV, Markdown |

---

## 🔧 Configuration Options

### Storage Settings
```python
storage_dir = "scholarpython_research"  # Where to store research
```

### Search Parameters
```python
PAPERS_LIMIT = 50                # Papers per search iteration
MAX_ITERATIONS = 5               # Search refinement iterations
SATURATION_THRESHOLD = 0.95      # Stop searching at 95% saturation
```

### Quality Score Weights
- Abstract quality: 25 pts
- Author collaboration: 20 pts
- Publication recency: 35 pts
- Citation impact: 40 pts
- **Total: 120 pts (capped at 100)**

---

## 📊 What Gets Stored

For each research topic, ScholAR stores:

```json
{
  "metadata.json": {        // Search info
    "topic": "string",
    "timestamp": "ISO-8601",
    "papers_count": "number",
    "contradictions_count": "number"
  },
  "research_data.json": {   // Complete analysis
    "papers": [],           // All papers found
    "contradictions": [],   // AI-detected conflicts
    "concepts": [],         // Key concepts
    "report": "markdown"    // AI synthesis
  },
  "papers.csv": {},         // Spreadsheet format
  "contradictions.json": {}, // Conflicts only
  "report.md": {}           // Markdown report
}
```

Local storage is **private and offline** - no cloud uploads.

---

## 🤖 How the Agent Works

1. **Initial Search**: Searches for papers on main topic
2. **Concept Extraction**: Identifies key concepts from papers
3. **Recursive Search**: Searches related concepts to find more papers
4. **Saturation Detection**: Stops when new papers plateau (95% similarity)
5. **Contradiction Analysis**: LLM identifies conflicting findings
6. **Report Generation**: Synthesizes all findings into readable analysis

**Result**: Comprehensive literature review in 60-120 seconds

---

## 📈 Quality Scoring Formula

**Total Score = Abstract (25) + Authors (20) + Recency (35) + Citations (40)**

### Abstract Quality
- 200+ chars: 25 pts ✓ Comprehensive
- 100-200 chars: 18 pts ✓ Detailed
- < 100 chars: 10 pts ✓ Has abstract
- None: 0 pts

### Author Collaboration
- 5+ authors: 20 pts (high collaboration)
- 3-4 authors: 16 pts
- 2 authors: 12 pts
- 1 author: 8 pts
- None: 0 pts

### Publication Recency
- 2024: 35 pts (cutting edge)
- 2022-2023: 30 pts (very recent)
- 2019-2021: 22 pts (recent)
- 2014-2018: 12 pts (classical)
- < 2014: 5 pts (foundational)

### Citation Impact
- 100+ citations: 40 pts (landmark)
- 50-99: 35 pts (highly influential)
- 21-49: 28 pts (influential)
- 11-20: 18 pts
- 1-10: 8 pts
- 0: 2 pts (new paper)

---

## ⚙️ Troubleshooting

### Port Already in Use
```bash
# Automatic solution (try ports 8501-8510)
python launch.py

# Or manually specify port
streamlit run app/streamlit_app.py --server.port 8502
```

### Empty PDF Generated
- Ensure report markdown is not empty
- Check LLM API connectivity
- Verify PDF generation in console output

### Cache Not Loading
- Check `scholarpython_research/research_history.db`
- Verify topic spelling (check cache history)
- Use "🔄 Force New" to bypass cache

### LLM Rate Limit
- System automatically falls back to mock data
- Wait 60 seconds before next search
- Verify `OPENROUTER_API_KEY` is set

---

## 🔐 Privacy & Data

- ✅ **100% Local Storage**: All data stored locally in SQLite
- ✅ **No Cloud Upload**: Papers never sent to external servers
- ✅ **Offline Capable**: Works without internet after first search
- ✅ **Own API Keys**: Uses your own OpenRouter/Semantic Scholar keys
- ✅ **Data Control**: Delete searches anytime from "Saved Research" tab

---

## 📝 Example Searches

Try these topics to see ScholAR in action:

- "Machine Learning in Healthcare"
- "Blockchain Security"
- "Deep Learning Natural Language Processing"
- "Quantum Computing Applications"
- "Climate Change Mitigation"
- "COVID-19 Vaccine Development"
- "Renewable Energy Systems"

---

## 🤝 Contributing

Contributions welcome! Areas for enhancement:

- [ ] Comparison of 2+ research topics
- [ ] Author co-citation networks
- [ ] Interactive contradiction resolution
- [ ] Mobile app (Flutter/PWA)
- [ ] API endpoints for integration
- [ ] Support for more paper databases

---

## 📄 License

MIT License - See LICENSE file for details

---

## 📞 Support

**Issues or Questions?**
- Check troubleshooting section above
- Review error messages in console
- Verify API keys are set correctly
- Ensure internet connection for API calls

**Report Bugs:**
- Describe search topic attempted
- Provide error message text
- Include console output
- Note which tab(s) affected

---

## 🎯 Future Roadmap

- [ ] **Mobile App**: Flutter/React Native versions
- [ ] **Team Collaboration**: Share research workspace
- [ ] **API Integration**: RESTful API for 3rd-party apps
- [ ] **Advanced Filtering**: More search refinement options
- [ ] **Citation Networks**: Visual paper citation graphs
- [ ] **Real-time Updates**: Subscribe to topic monitoring
- [ ] **AI Chat Interface**: Natural language research queries

---

**Built with ❤️ for researchers, students, and curious minds**

*Version 2.0 | Last Updated: 2024*
├── docs/                  # Documentation
│   ├── START_HERE.md     # Quick start guide
│   ├── SETUP.txt         # Setup instructions
│   ├── QUICKSTART.txt    # Quick reference
│   ├── UPDATES.md        # Recent changes
│   └── PROJECT_SUMMARY.txt # Full project overview
│
├── tests/                 # Test files
│   └── test_agent.py     # Agent tests
│
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/scholarpython.git
cd scholarpython
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
python scripts/verify.py
```

### 3. Run the Application

```bash
# Windows
scripts/run.bat

# Linux/Mac
bash scripts/run.sh

# Or directly
streamlit run app/streamlit_app.py
```

Then open: `http://localhost:8501`

### 4. Try a Research Topic

Example: "Transformer Models"

## 💡 How It Works

### Phase 1: Iterative Search

1. Start with user query
2. Search Semantic Scholar
3. Extract concepts from results
4. Calculate saturation score
5. If low saturation, autonomously identify sub-topic
6. **Recursive search** on the sub-topic (up to 3 levels deep)
7. Stop when saturation reaches 85%

### Phase 2: Paper Enhancement

1. Extract methodology from each abstract
2. Extract main conclusions
3. Extract key concepts
4. Build concept map

### Phase 3: Analysis & Insight

1. **Contradiction Detection**: Use LLM to find conflicting claims
2. **Gap Analysis**: Identify what's missing
3. **Clustering**: Group papers by methodology
4. **Trend Analysis**: Methodology evolution by year

### Phase 4: Report Generation

1. Generate comprehensive markdown report
2. Create visualization dashboards
3. Generate grant proposal based on gaps
4. Provide "Devil's Advocate" critical review

## 📊 Technology Stack

| Component           | Technology               |
| ------------------- | ------------------------ |
| **Search Engine**   | Semantic Scholar API     |
| **LLM Provider**    | OpenRouter (free tier)   |
| **Frontend**        | Streamlit                |
| **Visualization**   | Plotly, Streamlit-Agraph |
| **Data Processing** | Pandas, NetworkX         |

## 🔑 Configuration

Edit `config.py` to adjust:

- `MAX_PAPERS_PER_SEARCH`: Results per API call (default: 20)
- `RECURSIVE_SEARCH_MAX_DEPTH`: Max search iterations (default: 3)
- `SATURATION_THRESHOLD`: When to stop (default: 85%)
- `BATCH_SIZE`: Papers per enhancement batch (default: 5)

## 🎓 API Keys Required

The system uses two FREE APIs:

### Semantic Scholar

Get key: https://www.semanticscholar.org/product/api
Add to `config.py`:

```python
SEMANTIC_SCHOLAR_API_KEY = "your_key_here"
```

### OpenRouter (Free Models)

Get key: https://openrouter.ai
Add to `config.py`:

```python
OPENROUTER_API_KEY = "your_key_here"
```

**Note**: Uses only free tier models!

## 🏆 Winning Features

### 1. Autonomy

- ✅ Decides what to search autonomously
- ✅ Decides when to stop (saturation detection)
- ✅ Decides next search direction (recursive deep-dive)

### 2. Transparency

- ✅ Full "Thought Log" showing agent decisions
- ✅ Real-time status updates
- ✅ Explanation of methodology choices

### 3. Intelligence

- ✅ Finds contradictions (not just summaries)
- ✅ Identifies research gaps (not just conclusions)
- ✅ Generates grant proposals (actionable insights)
- ✅ Devil's advocate review (critical analysis)

### 4. User Experience

- ✅ Clean Streamlit interface
- ✅ Interactive knowledge graph
- ✅ Downloadable reports
- ✅ Dashboard with metrics

## 📝 Example Usage

1. **Input**: "Federated Learning in Healthcare"
2. **Agent thinks**:
   - "Searching 'Federated Learning in Healthcare'..."
   - "Found 15 papers. Extracting concepts: differential privacy, edge computing, communication efficiency..."
   - "Noticed 'differential privacy' in 12/15 papers. Starting secondary search..."
   - "Results show diminishing novelty. Moving to analysis phase..."
3. **Output**:
   - 23 papers analyzed
   - 4 contradictions identified (e.g., "Paper A: DP necessary" vs "Paper B: DP overhead too high")
   - 5 research gaps discovered
   - Grant proposal: "Investigate post-quantum privacy in federated settings"

## 🐛 Troubleshooting

### "API Error: 403"

- Check API keys in `config.py`
- Ensure quota limits not exceeded
- Verify network connectivity

### "LLM Request Timed Out"

- OpenRouter may be slow, retry
- Use faster model for testing
- Check `LLM_TIMEOUT` in config.py

### "Import Error"

- Run `pip install -r requirements.txt`
- Check Python version (3.8+)
- Run `validate.py` to diagnose

## 📚 References

- [Semantic Scholar API](https://www.semanticscholar.org/product/api)
- [OpenRouter](https://openrouter.ai)
- [Streamlit Docs](https://docs.streamlit.io)
- [NetworkX](https://networkx.org)

## 🎉 Credits

**ScholAR** - Built for the Hackathon
Demonstrating autonomous AI research capability.

---

**Questions?** Check the code comments or run `validate.py` for system diagnostics.
"# SXAG039" 
#   S c h o l A R  
 